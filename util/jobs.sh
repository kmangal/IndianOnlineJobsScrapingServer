
echo ""
echo "Current Jobs"
echo ""
echo "--------------------------------------"
echo "Current time:"
date
echo "--------------------------------------"
echo ""

echo "TimesJobs Scrapes"
echo "===================================================="
ps -elfH | head -n 1; ps -elfH | grep -i timesjobs | grep -v grep | grep -v "ps -elfH"

echo ""
echo "Shine Scrapes"
echo "===================================================="
ps -elfH | head -n 1; ps -elfH | grep -i shine | grep -v grep | grep -v "ps -elfH"

echo ""
echo "TeamLease Scrapes"
echo "===================================================="
ps -elfH | head -n 1; ps -elfH | grep -i teamlease | grep -v grep | grep -v "ps -elfH"

echo ""
echo "Monster Scrapes"
echo "===================================================="
ps -elfH | head -n 1; ps -elfH | grep -i monster | grep -v grep | grep -v "ps -elfH"

echo ""

