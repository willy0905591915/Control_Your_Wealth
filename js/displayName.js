document.addEventListener("DOMContentLoaded", () => {
  display = document.getElementById("usernameDisplay");
  var username = sessionStorage.getItem("username");
  if (username) {
    display.textContent = username;
  } else {
    display.textContent = "Please Log In";
    window.location.href = "./login.html";
  }
});
