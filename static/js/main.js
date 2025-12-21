function init() {
    google.accounts.id.initialize({
        client_id: '436003760252-f35qfvprbpjef42v6ikra8l85kdi5tv9.apps.googleusercontent.com',
        callback: handleCredentialResponse,
        auto_select: true
    });

    google.accounts.id.renderButton(
        document.getElementById("google-button"),
        {
            theme: "outline",
            size: "large",
        }
    );

    google.accounts.id.prompt();
}

async function handleCredentialResponse(response) {
    const request = await fetch('/auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: response.credential
        })
    })
    const result = await request.json()
    if (result.status_code === 200) {
        window.location.href = '/dashboard';
    }
    else {
        alert(result.error);
    }
}

window.onload = init;