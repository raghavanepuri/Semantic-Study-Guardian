function collectMetaTags() {
    return {
        description: document.querySelector('meta[name="description"]')?.content || "",
        keywords: document.querySelector('meta[name="keywords"]')?.content || "",
        og_title: document.querySelector('meta[property="og:title"]')?.content || "",
        og_description: document.querySelector('meta[property="og:description"]')?.content || ""
    };
}

function collectPageData() {
    return {
        study_goal: "Operating Systems", // Temporary placeholder goal
        url: window.location.href,
        title: document.title,
        meta_tags: collectMetaTags(),
        visible_text: document.body.innerText.slice(0, 1000), // Grab the first 1000 characters to prevent bloat
        transcript: null
    };
}

async function sendToBackend(pageData) {
    try {
        const response = await fetch("http://127.0.0.1:8000/classify", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(pageData)
        });
        const data = await response.json();
        console.log("Guardian Judgment Received:", data);
        
        // If the backend returns a BLOCK decision, throw an immediate alert for our prototype
        if (data.decision === "BLOCK") {
            alert(`⚠️ STUDY GUARDIAN BLOCK: \nReason: ${data.reason}`);
        }
    } catch (error) {
        console.error("Communication with Guardian server failed:", error);
    }
}

// Fire extraction instantly when the user finishes navigating to a site
const data = collectPageData();
sendToBackend(data);