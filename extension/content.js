(async function() {
  // 1. Fetch the user's real study goal from storage
  chrome.storage.local.get(['studyGoal'], async (data) => {
    const activeGoal = data.studyGoal || "General Studying"; 

    // 2. Extract meta tags to satisfy the backend model schema
    const metaTags = {};
    document.querySelectorAll('meta').forEach(meta => {
      const name = meta.getAttribute('name') || meta.getAttribute('property');
      const content = meta.getAttribute('content');
      if (name && content) {
        metaTags[name] = content;
      }
    });

    // 3. Construct the payload perfectly matching WebPageRequest
    const payload = {
      study_goal: activeGoal,
      url: window.location.href,
      title: document.title,
      meta_tags: metaTags, // Added to fix the 422 error!
      visible_text: document.body.innerText || "",
      transcript: null     // Optional field set to null explicitly
    };

    try {
      const response = await fetch("http://localhost:8000/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const result = await response.json();
        
        // 4. HARD BLOCK: Wipes out the page if the AI says BLOCK
        if (result.decision === "BLOCK") {
          document.documentElement.innerHTML = `
            <html style="background: #111827; color: white; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0;">
              <div style="text-align: center; max-width: 600px; padding: 40px; border: 2px solid #ef4444; border-radius: 12px; background: #1f2937; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5);">
                <h1 style="color: #ef4444; font-size: 2.5rem; margin-bottom: 10px;">🛑 ACCESS DENIED</h1>
                <h3 style="color: #9ca3af; font-weight: normal; margin-bottom: 25px;">Semantic Study Guardian Framework</h3>
                <p style="font-size: 1.2rem; line-height: 1.6; background: #374151; padding: 15px; border-radius: 6px; border-left: 5px solid #ef4444;">
                  <strong>Reason:</strong> ${result.reason}
                </p>
                <p style="margin-top: 20px; color: #6b7280; font-size: 0.9rem;">
                  Current Locked Target: <span style="color: #a855f7; font-weight: bold;">${activeGoal}</span>
                </p>
              </div>
            </html>
          `;
        }
      }
    } catch (err) {
      console.error("Study Guardian failed to evaluate page traffic:", err);
    }
  });
})();