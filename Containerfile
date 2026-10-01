FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mmif-storage-mv==0.2.0rc3

CMD ["start_api", "--dir", "/data"]
