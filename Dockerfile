# One-command reproduction of everything that does not need the source archives.
#
#   docker build -t veremi-audit workspace
#   docker run --rm veremi-audit
#
# The image carries the code, the result tables and the derived corpus evidence.
# It deliberately does not carry the VeReMi archives: they are 12 GB, they are not
# ours to redistribute, and they are one Zenodo download away. Everything that can
# be checked without them is checked here.
#
# To reproduce the experiments themselves rather than verify the shipped outputs,
# mount the archives and follow workspace/REPRODUCE.md:
#
#   docker run --rm -v /path/to/datasets:/work/workspace/datasets veremi-audit \
#       python -u workspace/sybilbench/exp9_cascade.py

FROM python:3.13-slim

WORKDIR /work

# pinned to the versions the released numbers were produced with
COPY requirements.txt /work/workspace/requirements.txt
RUN pip install --no-cache-dir -r /work/workspace/requirements.txt

COPY . /work/workspace/

# the corpus index lives beside the workspace in the source tree
RUN if [ -f /work/workspace/index.csv ]; then cp /work/workspace/index.csv /work/; fi

# fail the build if the shipped artefact does not verify
RUN python workspace/verify/v2_metrics.py \
 && python workspace/verify/v14_match_matrix.py --verify \
 && python workspace/paper/assemble.py \
 && python workspace/paper/check_sentences.py \
 && python workspace/paper/check_refs.py \
 && python workspace/paper/check_claims.py

CMD ["python", "workspace/verify/v19_table_reproduction.py"]
