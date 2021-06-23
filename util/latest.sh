
echo ""
echo "Latest Scrapes"
echo ""
echo "------------------------------------------"
echo "Current Time:"
date
echo "------------------------------------------"
echo ""

echo "Shine Scrapes"
echo "---------------------------------------------"
echo "Main Page:"
ls ~/shine/output/mainpage/ -lht | head -n5
echo "---------------------------------------------"
echo "Details:"
ls ~/shine/output/details/ -lht | head -n5

echo ""
echo "TimesJobs Scrapes"
echo "---------------------------------------------"
echo "Main Page:"
ls ~/timesjobs/output/mainpage/ -lht | head -n5
echo "---------------------------------------------"
echo "Details:"
ls ~/timesjobs/output/details/ -lht | head -n5

echo ""
echo "TeamLease Scrapes"
echo "---------------------------------------------"
echo "Main Page:"
ls ~/teamlease/output/mainpage/ -lht | head -n5
echo "---------------------------------------------"
echo "Details:"
ls ~/teamlease/output/details/ -lht | head -n5

