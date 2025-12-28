#!/bin/bash
# Quick progress checker for Algorithm 2
# Usage: ./check_progress.sh

SAVE_DIR="save"

echo "=========================================="
echo "Algorithm 2 Progress Report"
echo "=========================================="

echo ""
echo "MQ2007 Status:"
echo "----------------------------------------"
for seed in 1 2 3 4 5; do
    count=$(find ${SAVE_DIR}/MQ2007 -name "*seed${seed}*.pkl" 2>/dev/null | wc -l)
    percent=$((count * 100 / 270))
    
    if [ $count -eq 0 ]; then
        status="❌ Not started"
    elif [ $count -lt 270 ]; then
        status="🔄 In progress"
    else
        status="✅ Complete"
    fi
    
    printf "Seed %d: %s (%3d/270 files = %3d%%)\n" $seed "$status" $count $percent
done

echo ""
echo "MSLR10K Status:"
echo "----------------------------------------"
for seed in 1 2 3; do
    count=$(find ${SAVE_DIR}/MSLR10K -name "*seed${seed}*.pkl" 2>/dev/null | wc -l)
    percent=$((count * 100 / 270))
    
    if [ $count -eq 0 ]; then
        status="❌ Not started"
    elif [ $count -lt 270 ]; then
        status="🔄 In progress"
    else
        status="✅ Complete"
    fi
    
    printf "Seed %d: %s (%3d/270 files = %3d%%)\n" $seed "$status" $count $percent
done

echo ""
echo "Summary:"
echo "----------------------------------------"
mq2007_total=$(find ${SAVE_DIR}/MQ2007 -name "*.pkl" 2>/dev/null | wc -l)
mslr10k_total=$(find ${SAVE_DIR}/MSLR10K -name "*.pkl" 2>/dev/null | wc -l)

echo "MQ2007 total:  $mq2007_total files"
echo "MSLR10K total: $mslr10k_total files"

echo ""
echo "Target for paper (minimum):"
if [ $mq2007_total -ge 810 ]; then
    echo "  MQ2007 seeds 1-3: ✅ Ready ($mq2007_total/810 files)"
else
    echo "  MQ2007 seeds 1-3: ⏳ Need $((810 - mq2007_total)) more files"
fi

echo ""
echo "Running processes:"
ps aux | grep -E "(train.py|unlearn.py)" | grep -v grep | wc -l | xargs -I {} echo "  {} active Python processes"

echo ""
echo "=========================================="

