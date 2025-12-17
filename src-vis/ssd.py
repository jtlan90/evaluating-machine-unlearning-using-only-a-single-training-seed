"""
This file is used for the Selective Synaptic Dampening method
Strategy files use the methods from here
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset, dataset
from torch.autograd import Variable
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import torch.optim as optim
import time
import copy
import os
import pdb
import math
import shutil
from torch.utils.data import DataLoader
import wandb
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from typing import Dict, List

###############################################
# Clean implementation
###############################################


class ParameterPerturber:
    def __init__(
        self,
        model,
        opt,
        device="cuda" if torch.cuda.is_available() else "cpu",
        parameters=None,
    ):
        self.model = model
        self.opt = opt
        self.device = device
        self.alpha = None
        self.xmin = None

        print(parameters)
        self.lower_bound = parameters["lower_bound"]
        self.exponent = parameters["exponent"]
        self.magnitude_diff = parameters["magnitude_diff"]  # unused
        self.min_layer = parameters["min_layer"]
        self.max_layer = parameters["max_layer"]
        self.forget_threshold = parameters["forget_threshold"]
        self.dampening_constant = parameters["dampening_constant"]
        self.selection_weighting = parameters["selection_weighting"]

    def get_layer_num(self, layer_name: str) -> int:
        layer_id = layer_name.split(".")[1]
        if layer_id.isnumeric():
            return int(layer_id)
        else:
            return -1

    def zerolike_params_dict(self, model: torch.nn) -> Dict[str, torch.Tensor]:
        """
        Taken from: Avalanche: an End-to-End Library for Continual Learning - https://github.com/ContinualAI/avalanche
        Returns a dict like named_parameters(), with zeroed-out parameter valuse
        Parameters:
        model (torch.nn): model to get param dict from
        Returns:
        dict(str,torch.Tensor): dict of zero-like params
        """
        return dict(
            [
                (k, torch.zeros_like(p, device=p.device))
                for k, p in model.named_parameters()
            ]
        )

    def fulllike_params_dict(
        self, model: torch.nn, fill_value, as_tensor: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Returns a dict like named_parameters(), with parameter values replaced with fill_value

        Parameters:
        model (torch.nn): model to get param dict from
        fill_value: value to fill dict with
        Returns:
        dict(str,torch.Tensor): dict of named_parameters() with filled in values
        """

        def full_like_tensor(fillval, shape: list) -> list:
            """
            recursively builds nd list of shape shape, filled with fillval
            Parameters:
            fillval: value to fill matrix with
            shape: shape of target tensor
            Returns:
            list of shape shape, filled with fillval at each index
            """
            if len(shape) > 1:
                fillval = full_like_tensor(fillval, shape[1:])
            tmp = [fillval for _ in range(shape[0])]
            return tmp

        dictionary = {}

        for n, p in model.named_parameters():
            _p = (
                torch.tensor(full_like_tensor(fill_value, p.shape), device=self.device)
                if as_tensor
                else full_like_tensor(fill_value, p.shape)
            )
            dictionary[n] = _p
        return dictionary

    def subsample_dataset(self, dataset: dataset, sample_perc: float) -> Subset:
        """
        Take a subset of the dataset

        Parameters:
        dataset (dataset): dataset to be subsampled
        sample_perc (float): percentage of dataset to sample. range(0,1)
        Returns:
        Subset (float): requested subset of the dataset
        """
        sample_idxs = np.arange(0, len(dataset), step=int((1 / sample_perc)))
        return Subset(dataset, sample_idxs)

    def split_dataset_by_class(self, dataset: dataset) -> List[Subset]:
        """
        Split dataset into list of subsets
            each idx corresponds to samples from that class

        Parameters:
        dataset (dataset): dataset to be split
        Returns:
        subsets (List[Subset]): list of subsets of the dataset,
            each containing only the samples belonging to that class
        """
        n_classes = len(set([target for _, target in dataset]))
        subset_idxs = [[] for _ in range(n_classes)]
        for idx, (x, y) in enumerate(dataset):
            subset_idxs[y].append(idx)

        return [Subset(dataset, subset_idxs[idx]) for idx in range(n_classes)]

    def calc_importance(self, dataloader: DataLoader) -> Dict[str, torch.Tensor]:
        """
        Adapated from: Avalanche: an End-to-End Library for Continual Learning - https://github.com/ContinualAI/avalanche
        Calculate per-parameter, importance
            returns a dictionary [param_name: list(importance per parameter)]
        Parameters:
        DataLoader (DataLoader): DataLoader to be iterated over
        Returns:
        importances (dict(str, torch.Tensor([]))): named_parameters-like dictionary containing list of importances for each parameter
        """
        criterion = nn.CrossEntropyLoss()  # Define cross-entropy loss function for classification tasks
        importances = self.zerolike_params_dict(self.model)  # Initialize dictionary with zero tensors matching parameter shapes
        for batch in dataloader:  # Iterate through each batch in the dataloader
            x, _, y = batch  # Unpack the batch: x=inputs, y=class labels (middle element is ignored)
            x, y = x.to(self.device), y.to(self.device)  # Move data to the specified device (CPU/GPU)
            self.opt.zero_grad()  # Clear any existing gradients in the optimizer
            out = self.model(x)  # Forward pass: get model predictions
            loss = criterion(out, y)  # Calculate loss between predictions and true labels
            loss.backward()  # Compute gradients of loss with respect to model parameters

            for (k1, p), (k2, imp) in zip(
                self.model.named_parameters(), importances.items()  # Iterate through model parameters and importance tensors
            ):
                if p.grad is not None:  # Check if parameter has gradients (some may not require gradients)
                    imp.data += p.grad.data.clone().pow(2)  # Accumulate squared gradients as importance measure

        # average over mini batch length
        for _, imp in importances.items():  # Iterate through all importance tensors
            imp.data /= float(len(dataloader))  # Normalize by number of batches to get average importance
        return importances  # Return dictionary mapping parameter names to their importance tensors

    def calc_importance_loss_free(self, dataloader: DataLoader) -> Dict[str, torch.Tensor]:
        """
        Adapated from: Avalanche: an End-to-End Library for Continual Learning - https://github.com/ContinualAI/avalanche
        Calculate per-parameter, importance
            returns a dictionary [param_name: list(importance per parameter)]
        Parameters:
        DataLoader (DataLoader): DataLoader to be iterated over
        Returns:
        importances (dict(str, torch.Tensor([]))): named_parameters-like dictionary containing list of importances for each parameter
        """
        criterion = nn.CrossEntropyLoss()  # Define cross-entropy loss function for classification tasks
        importances = self.zerolike_params_dict(self.model)  # Initialize dictionary with zero tensors matching parameter shapes
        for batch in dataloader:  # Iterate through each batch in the dataloader
            x, _, y = batch  # Unpack the batch: x=inputs, y=class labels (middle element is ignored)
            x, y = x.to(self.device), y.to(self.device)  # Move data to the specified device (CPU/GPU)
            self.opt.zero_grad()  # Clear any existing gradients in the optimizer
            out = self.model(x)  # Forward pass: get model predictions
            loss = torch.norm(out, p="fro", dim=1).pow(2).mean()  # Calculate loss free importance
            loss.backward()  # Compute gradients of loss with respect to model parameters

            for (k1, p), (k2, imp) in zip(
                self.model.named_parameters(), importances.items()  # Iterate through model parameters and importance tensors
            ):
                if p.grad is not None:  # Check if parameter has gradients (some may not require gradients)
                    imp.data += p.grad.data.clone().abs()  # Accumulate squared gradients as importance measure

        # average over mini batch length
        for _, imp in importances.items():  # Iterate through all importance tensors
            imp.data /= float(len(dataloader))  # Normalize by number of batches to get average importance
        return importances  # Return dictionary mapping parameter names to their importance tensors



    def modify_weight(
        self,
        original_importance: List[Dict[str, torch.Tensor]],
        forget_importance: List[Dict[str, torch.Tensor]],
    ) -> None:
        """
        Perturb weights based on the SSD equations given in the paper
        Parameters:
        original_importance (List[Dict[str, torch.Tensor]]): list of importances for original dataset
        forget_importance (List[Dict[str, torch.Tensor]]): list of importances for forget sample
        threshold (float): value to multiply original imp by to determine memorization.

        Returns:
        None

        """

        with torch.no_grad():  # Disable gradient tracking to save memory and computation
            for (n, p), (oimp_n, oimp), (fimp_n, fimp) in zip(
                self.model.named_parameters(),  # Iterate through model parameters with their names
                original_importance.items(),    # Iterate through original importance values (from full dataset)
                forget_importance.items(),      # Iterate through forget importance values (from forget set)
            ):
                # Synapse Selection with parameter alpha
                oimp_norm = oimp.mul(self.selection_weighting)  # Scale original importance by alpha (selection_weighting)
                locations = torch.where(fimp > oimp_norm)       # Find parameters where forget importance > scaled original importance
                #   f(11) / o(2) 
                #   f(11) / o(2)  * alpha(5) 
                # Synapse Dampening with parameter lambda
                weight = ((oimp.mul(self.dampening_constant)).div(fimp)).pow(  # Calculate dampening factor: (λ*original_imp/forget_imp)^exponent
                    self.exponent
                )
                update = weight[locations]  # Extract dampening factors only for selected parameters
                
                # Bound by 1 to prevent parameter values to increase.
                min_locs = torch.where(update > self.lower_bound)  # Find locations where dampening factor > lower_bound (1)
                update[min_locs] = self.lower_bound                # Cap those dampening factors to lower_bound (1)
                p[locations] = p[locations].mul(update)            # Apply dampening: multiply selected parameters by their dampening factors


