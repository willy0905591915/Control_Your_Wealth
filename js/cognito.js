// cognito.js
// import "https://unpkg.com/amazon-cognito-identity-js/dist/amazon-cognito-identity.min.js";
// import "https://sdk.amazonaws.com/js/aws-sdk-2.1030.0.min.js";
import config from "./config.js";

AWS.config.region = "us-east-1"; // Your Cognito Region

const poolData = {
  UserPoolId: config.UserPoolId,
  ClientId: config.ClientId,
};

const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

export async function signUp(username, email, password) {
  var attributeList = [];
  var dataEmail = {
    Name: "email",
    Value: email,
  };
  var attributeEmail = new AmazonCognitoIdentity.CognitoUserAttribute(
    dataEmail
  );
  attributeList.push(attributeEmail);
  userPool.signUp(
    username,
    password,
    attributeList,
    null,
    function (err, result) {
      if (err) {
        alert(err.message || JSON.stringify(err));
        return;
      }
      var cognitoUser = result.user;
      alert(
        "Registering for " +
          cognitoUser.getUsername() +
          ", check email for an verification code"
      );
    }
  );
}

export async function confirmSignUp(username, code) {
  var userData = {
    Username: username,
    Pool: userPool,
  };

  var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
  cognitoUser.confirmRegistration(code, true, function (err, result) {
    if (err) {
      alert(err.message || JSON.stringify(err));
      return;
    }
    alert("Registration Completed!");
  });
}

export async function signIn(username, password) {
  var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails({
    Username: username,
    Password: password,
  });

  var userData = {
    Username: username,
    Pool: userPool,
  };

  var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

  return new Promise((resolve, reject) => {
    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: function (result) {
        // console.log("Access Token: " + result.getAccessToken().getJwtToken());
        resolve(result); // Optionally resolve with full result if needed elsewhere
      },
      onFailure: function (err) {
        console.error(err.message || JSON.stringify(err));
        reject(err); // Reject the promise with the error
      },
    });
  });
}

export async function signOut() {
  const username = sessionStorage.getItem("username");
  if (username) {
    var userData = {
      Username: username,
      Pool: userPool,
    };
    var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
    cognitoUser.getSession((err, result) => {
      if (err) {
        console.error(err.message);
        return;
      }
      if (result) {
        cognitoUser.globalSignOut({
          onSuccess: function (result) {
            alert("Successfully Logged Out!");
            sessionStorage.removeItem("username");
            sessionStorage.removeItem("idToken");
            sessionStorage.removeItem("accessToken");
            window.location.href = "/login.html";
          },
          onFailure: function (err) {
            console.error(err.message || JSON.stringify(err));
          },
        });
      }
    });
  } else {
    alert("No user currently...");
  }
}
// TODO: add logout function
