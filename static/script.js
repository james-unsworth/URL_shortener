const form = document.getElementById("urlform");
form.addEventListener("submit", async function(event){
    event.preventDefault()
    const input = document.getElementById("url");
    input.removeAttribute("aria-invalid");
    const errorEl = document.getElementById("error");
    errorEl.textContent = "";
    const result = document.getElementById("result")
    result.textContent = "";
    const urlValue = document.getElementById("url").value.trim();
    const urlObj = {
      url: urlValue
    };

try {
  const response = await fetch("/shorten", { 
    method: "POST", 
    headers: {
    'Content-Type': 'application/json'
    },  
    body: JSON.stringify(urlObj)
  }
  );

  const data = await response.json();
  if (response.ok) {
    const full_url = window.location.origin + "/" + data.short_url;
    const a = document.createElement("a");
    a.href = full_url;
    a.textContent = full_url;
    result.replaceChildren(a);
  }
  else {
    input.setAttribute("aria-invalid", "true");
    errorEl.textContent = data.err_msg;
  }
} catch (err) {
    input.setAttribute("aria-invalid", "true");
    errorEl.textContent = "Couldn't reach the server. Please try again.";
  }
});   
