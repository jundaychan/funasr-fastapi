# funasr-fastapi
funasr语音转文字的简单api版本，funasr+fastapi，方便部署在服务器上

1. 在服务器上部署[FUNASR](https://github.com/modelscope/FunASR/blob/main/runtime/docs/SDK_advanced_guide_offline_zh.md),建议docker一键部署
2. 更改.env中的文件,注意将asr服务的ip换成自己的服务器ip，redis的host换成asr-redis
3. docker部署即可，docker-compose up -d --build 
