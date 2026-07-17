function collectMetaTags() {
    return {
        description:
            document.querySelector('meta[name="description"]')?.content || "",

        keywords:
            document.querySelector('meta[name="keywords"]')?.content || "",

        og_title:
            document.querySelector('meta[property="og:title"]')?.content || "",

        og_description:
            document.querySelector('meta[property="og:description"]')?.content || "",

        og_type:
            document.querySelector('meta[property="og:type"]')?.content || ""
    };
}

function collectPageData() {
    return {
        study_goal: "Learn Operating Systems",

        url: window.location.href,

        title: document.title,

        meta_tags: collectMetaTags(),

        visible_text: document.body.innerText,

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

        console.log("Response from backend:");
        console.log(data);

    } catch (error) {
        console.error("Error communicating with backend:", error);
    }
}

const pageData = collectPageData();

sendToBackend(pageData);