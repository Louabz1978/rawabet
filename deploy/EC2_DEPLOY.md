# Rawabet EC2 Deploy

Use this after pulling the latest code on EC2.

```bash
cd /home/ec2-user/rawabet

npm install --prefix frontend
npm run build --prefix frontend

sudo cp deploy/nginx/rawabet.conf /etc/nginx/conf.d/rawabet.conf
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart rawabet-backend
```

Check the backend and uploads route:

```bash
curl -I http://127.0.0.1:4000/api/health
curl -I http://rawabet-sy.com/api/health
curl -I http://rawabet-sy.com/uploads/YOUR_UPLOADED_FILE_NAME
```

`/uploads/...` must return the file content type, such as `image/jpeg` or `application/pdf`.
If it returns `text/html`, Nginx is serving the frontend instead of proxying uploads to FastAPI.
