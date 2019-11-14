# Welcome to Appshare

Appshare is a smiple application for use to share secured way files and urls


## Demo:
Application is available under link: [https://appshare.herokuapp.com/](https://appshare.herokuapp.com/). Only resources retrieval is available for unauthorized users.


## Preconditions:
* Docker
* Docker-compose


## Usage
Make file is provided to help with developing

### Start application:

1. Create and image and run working django server
```bash
make start
```

2. Run migrations

```bash
make migrate
```

3. Create superuser:
```bash
make createsuperuser
```

4. Stop container:
```bash
make stop
```


# Extras:

### Unittests
1. Run unittests
```bash
make test
```

### Postman Collection
[Collection](Appshare.postman_collection.json)

## Note
Postman collection is prepared to automatically pass Authorization token in requests which required that.
Please have in mind that UploadFile need change in url path `<filename.ext>` and require a file upload. 
