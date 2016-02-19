FROM python:3.5.1-alpine

MAINTAINER Cheng Tianshi <213132955@seu.edu.cn>


RUN cd /srv \
    && git clone https://github.com/chengts95/iot_srtp.git \
    && cd iot_srtp/ \
    && pip3 install -r requirements.txt
WORKDIR /srv/iot_srtp/web
EXPOSE 8000

CMD ["python3", "/srv/iot_srtp/restful.py"]

