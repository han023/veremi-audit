cd "F:/d app/research paper"
while wmic process where "name='python.exe'" get commandline 2>/dev/null | grep -qE "download2|openaire.py"; do sleep 5; done
echo "=== phase1 done: $(ls pdfs|wc -l) pdfs"
python -u meta/retry.py
echo "=== after retry: $(ls pdfs|wc -l) pdfs"
python -u meta/build_index.py
