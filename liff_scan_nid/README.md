# LIFF


```
npm install axios
npm install --save @line/liff
npm run dev
npm run build
```

```
firebase login
firebase init
firebase deploy --only hosting:nid-scan
```


```
liff-cli app create \
   --channel-id 2006689746 \
   --name "NID Scan" \
   --endpoint-url https://nid-scan.web.app/ \
   --view-type full
```

```
 liff-cli app update \
   --liff-id 2006689746-nGpDmd7r \
   --channel-id 2006689746 \
   --endpoint-url  http://localhost:9000/
```

```
liff-cli serve \
   --liff-id 2006689746-nGpDmd7r \
   --url http://localhost:3000/ \
   --inspect
```

https://liff.line.me/2006689746-nGpDmd7r