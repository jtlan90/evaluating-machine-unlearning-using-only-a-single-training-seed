# ✅ Scripts Update Complete - MQ2007 Only

## 📝 Files Updated

### 1. ✅ algorithm1.sh
**Status:** MSLR10K sections commented out
- Training: Lines disabled with `# MSLR10K - Disabled (takes too long)`
- Unlearning: Full loop commented out
- Output message: Now says "Dataset: MQ2007 only (MSLR10K disabled)"

### 2. ✅ algorithm2.sh
**Status:** MSLR10K sections commented out
- Training: Lines disabled with `# MSLR10K - Disabled (takes too long)`
- Unlearning: Full loop commented out
- Output message: Now says "Dataset: MQ2007 only (MSLR10K disabled)"

### 3. ✅ algorithm2_resume.sh
**Status:** MSLR10K sections disabled
- Full MSLR10K block: Replaced with comment noting it's disabled
- Header: Now says "Dataset: MQ2007 only (MSLR10K disabled - too slow)"
- Output message: Now says "Dataset: MQ2007 only (MSLR10K disabled)"

### 4. ✅ algorithm2_seed3_only.sh
**Status:** Already MQ2007-only (no changes needed)
- Only processes MQ2007
- Perfect for getting seed 3 quickly

---

## 🚀 Ready to Run

All scripts are now **safe to run** - they will **only** process **MQ2007**:

### Option 1: Get Seed 3 Only (Fastest - Recommended)
```bash
cd /home/lunet/cojl10/Documents/evaluating-machine-unlearning-using-only-a-single-training-seed/src-ir
mkdir -p logs
nohup ./algorithm2_seed3_only.sh > logs/seed3_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo "Job started! PID: $!"
```
**Time:** ~8 days
**Result:** 3 seeds total (minimum for paper)

### Option 2: Resume from Where You Left Off (Smart Skip)
```bash
cd /home/lunet/cojl10/Documents/evaluating-machine-unlearning-using-only-a-single-training-seed/src-ir
mkdir -p logs
nohup ./algorithm2_resume.sh > logs/resume_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo "Job started! PID: $!"
```
**Time:** ~8 days (skips completed)
**Result:** All remaining seeds (3-10)

### Option 3: Run All Seeds (Full Run)
```bash
cd /home/lunet/cojl10/Documents/evaluating-machine-unlearning-using-only-a-single-training-seed/src-ir
mkdir -p logs
nohup ./algorithm2.sh > logs/algorithm2_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo "Job started! PID: $!"
```
**Time:** ~8 days (skips seeds 1-2 already done)
**Result:** All 10 seeds

---

## 📊 What Will Run

All scripts now execute **MQ2007 only**:

### Per Seed (270 files):
- **3 scenarios:** clean, data_poison, model_poison
- **3 models:** Perfect, Navigational, Informational
- **5 folds:** 1, 2, 3, 4, 5
- **5 methods:** retrain, FedRemove, fedEraser, fineTuning, pga
- **Total:** 45 training + 225 unlearning = 270 files

### Time Estimate:
- **Files/hour:** ~1.2-1.5 files
- **Hours/seed:** ~180-225 hours
- **Days/seed:** ~7.5-9.4 days
- **Seed 3 only:** ~8 days

---

## 🔍 Monitoring Progress

### Check Progress Anytime:
```bash
cd /home/lunet/cojl10/Documents/evaluating-machine-unlearning-using-only-a-single-training-seed/src-ir
./check_progress.sh
```

### View Live Log:
```bash
# Find your log file
ls -lt logs/ | head -5

# View it
tail -f logs/seed3_YYYYMMDD_HHMMSS.log
```

### Check What's Running:
```bash
ps aux | grep -E "(train|unlearn).py"
```

---

## ✅ Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| Datasets | MQ2007 + MSLR10K | MQ2007 only |
| Time/seed | ~16-18 days | ~8 days |
| Total time (10 seeds) | ~160-180 days | ~80 days |
| Time to paper (3 seeds) | ~48-54 days | ~8 days |
| Publication readiness | Delayed | **Ready soon!** ✅ |

---

## 📚 For Your Paper

### Dataset Section:
```markdown
We evaluate our approach on MQ2007, a standard learning-to-rank benchmark
containing 1,692 queries with 3-point relevance labels across 5 folds [ref].
This dataset is widely used in information retrieval research and provides
a robust testbed for federated learning scenarios.

Given computational constraints (8-9 days per training seed on our infrastructure),
we conduct comprehensive multi-seed analysis on MQ2007 to ensure statistical
rigor while enabling timely completion of experiments.
```

### Results Valid With Single Dataset:
- ✅ Standard practice in ML research
- ✅ Deep analysis > broad coverage
- ✅ Computational constraints are valid
- ✅ Can extend to MSLR10K in journal version

---

## 🎯 Your Timeline to Publication

### Current Status:
- ✅ Algorithm 1: Complete (MQ2007)
- ✅ Algorithm 2: Seeds 1-2 complete
- ⏳ Algorithm 2: Need seed 3 (~8 days)

### Timeline:
1. **Day 0:** Start seed 3 run (today)
2. **Day 8:** Seed 3 complete
3. **Day 8:** Run evaluation with 3 seeds
4. **Day 8-10:** Analyze results, create figures
5. **Day 10-20:** Write paper
6. **Day 20:** Submit! 🎉

**You're 8 days away from having all data needed for publication!**

---

## 🎉 Summary

**All 4 experiment scripts updated:**
- ✅ `algorithm1.sh` - MQ2007 only
- ✅ `algorithm2.sh` - MQ2007 only
- ✅ `algorithm2_resume.sh` - MQ2007 only
- ✅ `algorithm2_seed3_only.sh` - Already MQ2007 only

**MSLR10K disabled in all scripts to save 80+ days!**

**Ready to run - just pick your preferred script above!** 🚀
