# How to access APIs with authorized status

## Frontend side
Example at [test.html](./test.html)
1. Obtain ```idToken``` from ```sessionStorage```
```js
const idToken = sessionStorage.getItem("idToken");
```
2. Add ```idToken``` into request header: Authorization
```js
axios.get(testUrl, {
    headers: { Authorization: `Bearer ${idToken}` },
    params: {
        value1: value1,
    },
}).then().catch();
```

## Server side
Example at lambda: "test-lambda"  
1. Getting username:
```py
username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
```
2. Getting user email:
```py
email = event["requestContext"]["authorizer"]["claims"]["email"]
```
3. Getting request params, body, ...
See Cloud Watch Log Group: /aws/lambda/test-lambda for event format  

## Api Gateway
Example at resource: /test, METHOD = GET  
1. Protect resource and method with Cognito  
   1. Goto ```/your-resource/your-method``` in API Gateway Console  
   2. Goto ```Method request settings -> Edit```  
   3. Set ```Authorization``` to ```user-auth-safe```
2. Don't forget to enable CORS. If using `Lambda`, when return:
   ```
    return {
        'statusCode': 200,
        'headers': { 
            "Content-Type": "application/json",
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(json_object)
    }
   ```