
import { SharedContextManager } from "../session/shared-context-manager.js";
import { AuthManager } from "../auth/auth-manager.js";
import * as fs from 'fs';
import * as path from 'path';

import { execSync } from 'child_process';

// Force PERSISTENT profile for "Fully Automatic" experience (Login once, run forever)
process.env.NOTEBOOK_PROFILE_STRATEGY = 'persistent';

// SAFETY: Kill any existing Chrome processes to prevent "Exit Code 21" (Profile Locked) errors
try {
    console.log("🧹 Cleaning up old browser sessions...");
    execSync('taskkill /F /IM chrome.exe /T 2>NUL');
} catch (e) {
    // Ignore error if chrome wasn't running
}

async function main() {
    console.log("🚀 Starting NotebookLM Auto-Writer (Deep Search Mode)...");

    // Parse Arguments
    const args = process.argv.slice(2);
    const topicArgIndex = args.indexOf('--topic');
    const sourceArgIndex = args.indexOf('--source');

    const topic = topicArgIndex !== -1 ? args[topicArgIndex + 1] : "Agentic AI trends in 2026";
    let sourceArg = sourceArgIndex !== -1 ? args[sourceArgIndex + 1] : null;

    console.log(`📝 Topic: "${topic}"`);
    console.log(`📂 Source: ${sourceArg ? sourceArg : "AUTO WEB SEARCH"}`);

    // 1. Initialize Managers
    const authManager = new AuthManager();
    const contextManager = new SharedContextManager(authManager);

    try {
        // 2. Launch Browser (Visible Mode)
        console.log("🌐 Launching browser (Isolated Profile)...");
        const context = await contextManager.getOrCreateContext(true);
        const page = await context.newPage();

        // --- 2.5 Web Search Phase ---
        if (!sourceArg) {
            console.log("🔍 No source file provided. Searching Google for relevant content...");
            try {
                // Perform Google Search
                // Perform Google Search (Deep Search V2)
                console.log(`🔍 Searching: ${topic}`);
                await page.goto(`https://www.google.com/search?q=${encodeURIComponent(topic)}`, { waitUntil: 'domcontentloaded' });

                // Wait for results to stabilize (Generous wait for dynamic content)
                await page.waitForTimeout(5000);

                let foundUrl = "";
                // Selectors (Prioritize H3 titles, then generic results)
                const possibleSelectors = ['a:has(h3)', '#search .g a', '#rso a'];

                for (const sel of possibleSelectors) {
                    try {
                        const el = page.locator(sel).first();
                        await el.waitFor({ state: 'attached', timeout: 10000 });
                        const url = await el.getAttribute('href');

                        // Filter: Must be http, not google.com, not google.co.kr (just to be safe)
                        if (url && url.startsWith('http') && !url.includes('google.com') && !url.includes('google.co')) {
                            foundUrl = url;
                            break;
                        }
                    } catch { continue; }
                }

                if (foundUrl) {
                    sourceArg = foundUrl;
                    console.log(`✅ Found Web Source: ${sourceArg}`);
                } else {
                    throw new Error("Could not extract a valid URL from search results.");
                }
            } catch (e) {
                console.error("❌ Web search failed or timed out. Falling back to default file.");
                const fallbackPath = path.resolve("trends_2026.txt");
                console.log(`Checking fallback at: ${fallbackPath}`);

                if (fs.existsSync(fallbackPath)) {
                    console.log("⚠️ Using fallback file: trends_2026.txt");
                    sourceArg = fallbackPath; // Use absolute path
                } else {
                    throw new Error(`Search failed and no fallback file found at ${fallbackPath}`);
                }
            }
        }

        await page.goto("https://notebooklm.google.com/");

        // --- Login Helper: Auto-fill Email ---
        try {
            const emailInput = page.locator('input[type="email"]').first();
            // Short timeout to check if we are on login page
            if (await emailInput.isVisible({ timeout: 4000 })) {
                console.log("🔑 Login Page Detected!");
                console.log("🤖 Auto-filling email: tjddnn81@gmail.com");
                await emailInput.fill("tjddnn81@gmail.com");
                await page.keyboard.press('Enter');
                console.log("⏳ Please enter your password to complete login (Persistent Mode will remember this next time!)");
                // Wait extra time for user to finish login
                await page.waitForTimeout(5000);
            }
        } catch (e) {
            // Not on login page, proceed normal
        }

        // 3. Automated Setup (New Notebook)
        console.log("🤖 Auto-creating notebook...");

        try {
            // Handle "New Notebook" (English/Korean)
            const newBtn = page.locator('div[role="button"], button').filter({ hasText: /New Notebook|새 노트북/i }).first();

            console.log("⏳ Waiting for 'New Notebook' button (Please Log In if needed)...");
            // 2 minutes timeout for login
            await newBtn.waitFor({ state: 'visible', timeout: 120000 });
            await newBtn.click();
            console.log("✅ Clicked 'New Notebook'");
        } catch (e) {
            console.log("⚠️ Auto-click failed. Please click 'New Notebook' manually.");
        }

        // 4. Add Source (File or Website)
        try {
            console.log(`🤖 Adding Source: ${sourceArg}...`);

            if (sourceArg && sourceArg.startsWith('http')) {
                // ** Website Source Logic **
                console.log("🌐 Adding via Website Link...");

                // Wait for source panel to appear
                await page.waitForTimeout(3000);

                // Try multiple selectors for the Website/Link button
                const webBtnSelectors = [
                    'button:has-text("Website")',
                    'button:has-text("Link")',
                    'button:has-text("웹사이트")',
                    'div[role="button"]:has-text("Website")',
                    'div[role="button"]:has-text("Link")',
                    'div[role="button"]:has-text("웹사이트")',
                    '[data-test-id*="website"]',
                    '[data-test-id*="link"]'
                ];

                let clicked = false;
                for (const sel of webBtnSelectors) {
                    try {
                        const btn = page.locator(sel).first();
                        if (await btn.isVisible({ timeout: 3000 })) {
                            await btn.click();
                            clicked = true;
                            console.log(`✅ Clicked source button: ${sel}`);
                            break;
                        }
                    } catch { continue; }
                }

                if (!clicked) {
                    // Fallback: try clicking any source card that mentions web/link
                    const sourceCard = page.locator('[class*="source"], [class*="card"]').filter({ hasText: /Website|Link|웹|URL/i }).first();
                    await sourceCard.click().catch(() => { });
                }

                // Wait for dialog/modal
                await page.waitForTimeout(2000);

                // Find URL input - try multiple approaches
                const urlInputSelectors = [
                    'input[type="url"]',
                    'input[type="text"]',
                    'input[placeholder*="URL"]',
                    'input[placeholder*="http"]',
                    'input[placeholder*="링크"]',
                    'textarea'
                ];

                let urlFilled = false;
                for (const sel of urlInputSelectors) {
                    try {
                        const input = page.locator(`div[role="dialog"] ${sel}, [class*="modal"] ${sel}, [class*="dialog"] ${sel}`).first();
                        if (await input.isVisible({ timeout: 3000 })) {
                            await input.fill(sourceArg);
                            urlFilled = true;
                            console.log(`✅ Filled URL in: ${sel}`);
                            break;
                        }
                    } catch { continue; }
                }

                // Fallback: find any visible input
                if (!urlFilled) {
                    const anyInput = page.locator('input:visible').first();
                    await anyInput.fill(sourceArg).catch(() => { });
                }

                // Click Insert/Add button
                await page.waitForTimeout(1000);
                const addBtnSelectors = [
                    'button:has-text("Insert")',
                    'button:has-text("Add")',
                    'button:has-text("추가")',
                    'button:has-text("삽입")',
                    'div[role="button"]:has-text("Insert")',
                    'div[role="button"]:has-text("Add")',
                    'div[role="button"]:has-text("추가")'
                ];

                for (const sel of addBtnSelectors) {
                    try {
                        const btn = page.locator(sel).last();
                        if (await btn.isVisible({ timeout: 2000 })) {
                            await btn.click();
                            console.log(`✅ Clicked add button: ${sel}`);
                            break;
                        }
                    } catch { continue; }
                }

                console.log(`✅ Added Web Source: ${sourceArg}`);

                // Wait for source to be processed
                console.log("⏳ Waiting for NotebookLM to process source (30 seconds)...");
                await page.waitForTimeout(30000);

            } else {
                // ** File Upload Logic **
                const fileInput = page.locator('input[type="file"]').first();
                await fileInput.waitFor({ state: 'attached', timeout: 30000 });

                const filePath = path.resolve(sourceArg || "trends_2026.txt");
                if (fs.existsSync(filePath)) {
                    await fileInput.setInputFiles(filePath);
                    console.log(`✅ Uploaded: ${filePath}`);
                } else {
                    console.error(`❌ File not found: ${filePath}`);
                }

                // Wait for file to be processed
                await page.waitForTimeout(15000);
            }

        } catch (e) {
            console.log("⚠️ Auto-add source failed. Please add manually.", e);
        }

        // 5. Generate Content (Direct Page Automation - No BrowserSession needed)
        console.log("⏳ Waiting for notebook to load...");

        // Wait for page URL to change to a notebook
        await page.waitForURL(/notebook\//, { timeout: 45000 }).catch(() => {
            console.log("⚠️ URL didn't change to notebook. Trying to find chat input on current page...");
        });

        const notebookUrl = page.url();
        console.log(`🔗 Current URL: ${notebookUrl}`);

        // Wait for chat input to be available (with extended timeout for source processing)
        console.log("⏳ Waiting for chat input to be ready (source processing may take time)...");

        // Try multiple selectors for chat input
        const chatSelectors = [
            'textarea.query-box-input',
            'textarea[aria-label*="query" i]',
            'textarea[placeholder*="Ask" i]',
            'textarea:not([disabled])'
        ];

        let chatInput = null;
        for (let attempt = 0; attempt < 6; attempt++) {
            for (const sel of chatSelectors) {
                try {
                    const input = page.locator(sel).first();
                    if (await input.isVisible({ timeout: 3000 })) {
                        const isDisabled = await input.getAttribute('disabled');
                        if (!isDisabled) {
                            chatInput = input;
                            console.log(`✅ Found chat input: ${sel}`);
                            break;
                        } else {
                            console.log(`⏳ Chat input disabled, waiting...`);
                        }
                    }
                } catch { continue; }
            }
            if (chatInput) break;
            console.log(`⏳ Attempt ${attempt + 1}/6 - Chat not ready, waiting 5 seconds...`);
            await page.waitForTimeout(5000);
        }

        if (!chatInput) {
            console.log("⚠️ Could not find enabled chat input. Please generate content manually in the browser.");
            console.log("🔗 Open the notebook and ask: 'Write a blog post about: " + topic + "'");
            console.log("⏳ Browser will remain open for 60 seconds...");
            await page.waitForTimeout(60000);
            return;
        }

        // Type the blog request
        console.log("✍️  Writing content request...");
        const blogPrompt = `Write a blog post about: ${topic}. Based on the source I just added. Use emojis and markdown. Make it SEO-optimized, at least 1500 characters.`;

        await chatInput.click();
        await page.waitForTimeout(500);
        await chatInput.fill(blogPrompt);
        await page.waitForTimeout(500);

        // Submit
        await page.keyboard.press('Enter');
        console.log("📤 Submitted blog request!");

        // Wait for response
        console.log("⏳ Waiting for NotebookLM to generate response (60 seconds)...");
        await page.waitForTimeout(60000);

        // Try to extract response
        const responseSelectors = [
            '[class*="response"]',
            '[class*="answer"]',
            '[class*="message"]',
            '.markdown-content'
        ];

        let answer = "";
        for (const sel of responseSelectors) {
            try {
                const responses = await page.locator(sel).allTextContents();
                if (responses.length > 0) {
                    answer = responses[responses.length - 1];
                    break;
                }
            } catch { continue; }
        }

        if (answer && answer.length > 100) {
            console.log("\n\n✅ GENERATED CONTENT:\n");
            console.log(answer);

            // Save
            const outputPath = `output_${Date.now()}.md`;
            fs.writeFileSync(outputPath, answer);
            console.log(`\n💾 Saved to ${outputPath}`);
        } else {
            console.log("\n⚠️ Could not extract content automatically.");
            console.log("📋 Please copy the content manually from the browser.");
        }

        // Keep browser open for manual review
        console.log("⏳ Browser will remain open for 60 seconds for review...");
        await page.waitForTimeout(60000);

    } catch (error) {
        console.error("❌ Error:", error);
    }
}

main();
