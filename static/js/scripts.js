/*home html*/
function showLogin() {
  document.getElementById('login-form').classList.remove('hidden');
  document.getElementById('signup-form').classList.add('hidden');
  document.getElementById('loginBtn').classList.add('active');
  document.getElementById('signupBtn').classList.remove('active');
}

function showSignup() {
  document.getElementById('signup-form').classList.remove('hidden');
  document.getElementById('login-form').classList.add('hidden');
  document.getElementById('signupBtn').classList.add('active');
  document.getElementById('loginBtn').classList.remove('active');
}

/*household html*/
  function calculateCarbonFootprint() {
    const electricity = parseFloat(document.getElementById("electricity").value) || 0;
    const lpg = parseFloat(document.getElementById("lpg").value) || 0;
    const water_consumption = parseFloat(document.getElementById("water-consumption").value) || 0;
    const waste = parseFloat(document.getElementById("waste").value) || 0;
    const members = parseInt(document.getElementById("members").value) || 1;

    const elec_result = (electricity / members) * 0.0498;
    const lpg_result = (lpg / members) * 0.022454;
    const water_consumption_result = water_consumption * 0.0106;
    const waste_result = (waste / members) * 1.59;
    const total = elec_result + lpg_result + water_consumption_result + waste_result;

    document.getElementById("elec_result").value = elec_result.toFixed(2);
    document.getElementById("lpg_result").value = lpg_result.toFixed(2);
    document.getElementById("water_consumption_result").value = water_consumption_result.toFixed(2);
    document.getElementById("waste_result").value = waste_result.toFixed(2);
    document.getElementById("total").innerText = total.toFixed(2);
    }