
import { SharedContextManager } from "../session/shared-context-manager.js";
import { AuthManager } from "../auth/auth-manager.js";
import { BrowserSession } from "../session/browser-session.js";
import * as fs from 'fs';
import * as path from 'path';



import { execSync } from 'child_process';

// Force PERSISTENT profile for "Fully Automatic" experience
process.env.NOTEBOOK_PROFILE_STRATEGY = 'persistent';

// SAFETY: Kill any existing Chrome processes to prevent "Exit Code 21"
try {
    console.log("🧹 Cleaning up old browser sessions...");
    execSync('taskkill /F /IM chrome.exe /T 2>NUL');
} catch (e) {
    // Ignore error if chrome wasn't running
}

async function main() {
    console.log("🚀 Starting Blog Generation Automation (Isolated Profile)...");

    // 1. Initialize Managers
    const authManager = new AuthManager();
    const contextManager = new SharedContextManager(authManager);

    try {
        // We override headless to TRUE (which means SHOW BROWSER in some logic? Wait check implementation)
        // SharedContextManager.recreateContext(overrideHeadless):
        // const shouldBeHeadless = overrideHeadless !== undefined ? !overrideHeadless : CONFIG.headless;
        // So if I want SHOW BROWSER (NOT HEADLESS), shouldBeHeadless must be false.
        // !overrideHeadless = false => overrideHeadless = true.
        // So passing TRUE means SHOW BROWSER. 
        console.log("🌐 Launching browser (Visible Mode)...");
        const context = await contextManager.getOrCreateContext(true);

        // Create a page just to land on the home page
        const page = await context.newPage();
        await page.goto("https://notebooklm.google.com/");

        // --- AUTOMATION: Create Notebook & Upload ---
        console.log("🤖 Auto-creating notebook...");

        try {
            // 1. Click 'New Notebook' (Handle Korean "새 노트북")
            // Using locators that should work for both Grid and List view
            // The main "New Notebook" button usually has text.
            const newBtn = page.locator('div[role="button"], button').filter({ hasText: /New Notebook|새 노트북/i }).first();

            // Provide a generous timeout for page load/login (2 minutes to allow user to log in)
            console.log("⏳ Waiting for 'New Notebook' button (Please Log In if needed)...");
            await newBtn.waitFor({ state: 'visible', timeout: 120000 });
            await newBtn.click();
            console.log("✅ Clicked 'New Notebook'");
        } catch (e) {
            console.log("⚠️ Auto-click failed or timed out. Please click 'New Notebook' manually.");
        }

        try {
            // 2. Upload File
            console.log("🤖 Uploading source file...");
            // Wait for file input to appear (it's inside the 'Add source' area)
            const fileInput = page.locator('input[type="file"]').first();
            await fileInput.waitFor({ state: 'attached', timeout: 20000 });

            const filePath = path.resolve("trends_2026.txt");
            if (fs.existsSync(filePath)) {
                await fileInput.setInputFiles(filePath);
                console.log(`✅ Uploaded: ${filePath}`);
            } else {
                console.error(`❌ File not found: ${filePath}`);
            }

            // Wait for NotebookLM to process the file (UI animation)
            await page.waitForTimeout(5000);
        } catch (e) {
            console.log("⚠️ Auto-upload failed. Please upload 'trends_2026.txt' manually if needed.");
        }
        // --------------------------------------------

        // 3. Wait for User to Create/Select Notebook (Auto-detect URL)
        console.log("⏳ Waiting for you to navigate to a NotebookLM notebook...");
        let notebookUrl = "";

        while (true) {
            const pages = context.pages();
            const activePage = pages[pages.length - 1]; // Assume last active page
            if (activePage) {
                const url = activePage.url();
                if (url.includes("notebooklm.google.com/notebook/")) {
                    notebookUrl = url;
                    break;
                }
            }
            await new Promise(r => setTimeout(r, 1000));
        }

        if (!notebookUrl || !notebookUrl.startsWith("https://notebooklm")) {
            console.error("❌ Invalid URL provided. Exiting.");
            process.exit(1);
        }

        console.log(`\n✅ Using Notebook: ${notebookUrl}`);
        console.log("🤖 Starting automated blog generation...");

        // 4. Initialize Session
        // We use a dummy session ID 'blog_gen_task'
        const session = new BrowserSession("blog_gen_task", contextManager, authManager, notebookUrl);
        await session.init();

        // 5. Generate Content
        const topics = [
            "Agentic AI와 2026년의 변화에 대해 블로그 글을 써줘. 서론, 본론, 결론으로 나누고 이모지를 사용해.",
            "2016년 노스텔지어 트렌드('2026 is the new 2016')에 대해 블로그 글을 써줘. 재미있게 작성해줘.",
            "구글 Deep Search와 검색의 변화(Answer Engine)에 대해 블로그 글을 전문적으로 써줘."
        ];

        let combinedContent = "# Generated Blog Posts\n\n";

        for (const [index, topic] of topics.entries()) {
            console.log(`\n✍️  Writing Post ${index + 1}/3...`);
            // Pass a simple progress callback
            const answer = await session.ask(topic, async (_status) => { process.stdout.write(`R`); });

            combinedContent += `## Blog Post ${index + 1}\n\n${answer}\n\n---\n\n`;
            console.log(`\n✅ Post ${index + 1} completed!`);
        }

        // 6. Save to File
        const outputPath = "generated_blog_posts_notebooklm.md";
        fs.writeFileSync(outputPath, combinedContent);

        console.log("\n" + "=".repeat(50));
        console.log(`🎉 SUCCESS! Blog posts saved to: ${outputPath}`);
        console.log("=".repeat(50));

    } catch (error) {
        console.error("❌ Error during execution:", error);
    } finally {
        // Cleanup? Maybe keep browser open for user to see, or close.
        // Let's close the context manager (which might close browser depending on logic)
        // process.exit(0);
    }
}

main();
