/**
 * NotebookLM Native Deep Research Auto-Writer
 * 
 * This script uses NotebookLM's built-in "Deep Research" feature to:
 * 1. Create a new notebook
 * 2. Use "Web" source with "Deep Research" mode
 * 3. AI automatically searches and adds sources (web, YouTube, etc.)
 * 4. Generate blog post from those sources
 */

import { chromium } from 'playwright-core';
import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

// Configuration
const CHROME_PROFILE_PATH = path.join(
    process.env.LOCALAPPDATA || 'C:\\Users\\tjddn\\AppData\\Local',
    'notebooklm-mcp', 'Data', 'chrome_profile'
);

async function main() {
    // Parse arguments
    const args = process.argv.slice(2);
    let topic = "빗썸 최신 뉴스"; // Default topic

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--topic' && args[i + 1]) {
            topic = args[i + 1];
            i++;
        }
    }

    console.log("🧹 Cleaning up old browser sessions...");
    try {
        execSync('taskkill /F /IM chrome.exe /T 2>nul', { stdio: 'ignore' });
    } catch { /* ignore */ }
    await new Promise(r => setTimeout(r, 2000));

    console.log("🚀 Starting NotebookLM Native Deep Research...");
    console.log(`📝 Topic: "${topic}"`);
    console.log("🔍 Mode: NotebookLM Built-in Deep Research\n");

    // Launch browser with persistent profile - use system Chrome
    const context = await chromium.launchPersistentContext(CHROME_PROFILE_PATH, {
        headless: false,
        channel: 'chrome', // Use system Chrome instead of bundled Chromium
        args: [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-first-run',
            '--no-default-browser-check'
        ],
        viewport: { width: 1400, height: 900 }
    });

    const page = await context.newPage();

    try {
        // 1. Navigate to NotebookLM
        console.log("🌐 Opening NotebookLM...");
        await page.goto('https://notebooklm.google.com/', { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(5000);

        // Check for login
        const needsLogin = await page.locator('input[type="email"]').isVisible({ timeout: 3000 }).catch(() => false);
        if (needsLogin) {
            console.log("🔑 Login required. Please log in manually...");
            console.log("⏳ Waiting up to 2 minutes for login...");
            await page.waitForURL('**/notebooklm.google.com/**', { timeout: 120000 });
        }

        // 2. Create New Notebook
        console.log("📓 Creating new notebook...");
        await page.waitForTimeout(3000);

        const newNotebookSelectors = [
            'button:has-text("New notebook")',
            'button:has-text("새 노트북")',
            'div[role="button"]:has-text("New notebook")',
            'div[role="button"]:has-text("새 노트북")',
            '[data-test-id*="new-notebook"]'
        ];

        for (const sel of newNotebookSelectors) {
            try {
                const btn = page.locator(sel).first();
                if (await btn.isVisible({ timeout: 3000 })) {
                    await btn.click();
                    console.log("✅ Clicked 'New Notebook'");
                    break;
                }
            } catch { continue; }
        }

        await page.waitForTimeout(4000);

        // 3. Click on "Add Source" or "Sources" panel
        console.log("📂 Looking for source options...");

        const addSourceSelectors = [
            'button:has-text("Add source")',
            'button:has-text("소스 추가")',
            'div:has-text("Add source")',
            '[aria-label*="Add source"]',
            '[aria-label*="소스 추가"]'
        ];

        for (const sel of addSourceSelectors) {
            try {
                const btn = page.locator(sel).first();
                if (await btn.isVisible({ timeout: 3000 })) {
                    await btn.click();
                    console.log(`✅ Clicked: ${sel}`);
                    break;
                }
            } catch { continue; }
        }

        await page.waitForTimeout(2000);

        // 4. Select "Web" or "Website" source type
        console.log("🌐 Selecting Web source type...");

        const webSourceSelectors = [
            'button:has-text("Web")',
            'button:has-text("웹")',
            'div[role="button"]:has-text("Web")',
            'div[role="button"]:has-text("Website")',
            '[data-test-id*="web"]'
        ];

        for (const sel of webSourceSelectors) {
            try {
                const btn = page.locator(sel).first();
                if (await btn.isVisible({ timeout: 3000 })) {
                    await btn.click();
                    console.log(`✅ Selected Web source: ${sel}`);
                    break;
                }
            } catch { continue; }
        }

        await page.waitForTimeout(2000);

        // 5. Look for "Deep Research" option
        console.log("🔬 Looking for Deep Research option...");

        const deepResearchSelectors = [
            'button:has-text("Deep Research")',
            'button:has-text("딥 리서치")',
            'button:has-text("Deep research")',
            'div[role="button"]:has-text("Deep Research")',
            '[data-test-id*="deep-research"]',
            'label:has-text("Deep Research")',
            'span:has-text("Deep Research")'
        ];

        let deepResearchFound = false;
        for (const sel of deepResearchSelectors) {
            try {
                const el = page.locator(sel).first();
                if (await el.isVisible({ timeout: 3000 })) {
                    await el.click();
                    console.log(`✅ Selected Deep Research: ${sel}`);
                    deepResearchFound = true;
                    break;
                }
            } catch { continue; }
        }

        // If Deep Research not found, try alternative approach
        if (!deepResearchFound) {
            console.log("⚠️ Deep Research button not found. Trying research input directly...");
        }

        await page.waitForTimeout(2000);

        // 6. Enter research topic
        console.log(`📝 Entering topic: "${topic}"...`);

        const inputSelectors = [
            'input[placeholder*="research"]',
            'input[placeholder*="리서치"]',
            'input[placeholder*="topic"]',
            'input[placeholder*="주제"]',
            'textarea[placeholder*="research"]',
            'input[type="text"]',
            'textarea'
        ];

        for (const sel of inputSelectors) {
            try {
                const input = page.locator(sel).first();
                if (await input.isVisible({ timeout: 3000 })) {
                    await input.fill(topic);
                    console.log(`✅ Entered topic in: ${sel}`);

                    // Press Enter or click Start button
                    await page.keyboard.press('Enter');
                    break;
                }
            } catch { continue; }
        }

        // 7. Wait for Deep Research to complete (can take several minutes)
        console.log("⏳ Waiting for Deep Research to find sources (this may take 1-2 minutes)...");

        // Wait for sources to appear or for research to complete
        await page.waitForTimeout(60000); // 1 minute initial wait

        // Check if sources were added
        const sourceCount = await page.locator('[class*="source"], [data-test-id*="source"]').count();
        console.log(`📚 Found ${sourceCount} sources`);

        if (sourceCount === 0) {
            console.log("⏳ Still waiting for sources... (30 more seconds)");
            await page.waitForTimeout(30000);
        }

        // 8. Generate blog post using chat
        console.log("✍️ Generating blog post...");
        console.log("⏳ Waiting for chat to be ready (sources need to be processed)...");

        // Wait for sources to be fully processed (chat becomes enabled)
        await page.waitForTimeout(15000);

        const chatInputSelectors = [
            'textarea.query-box-input',
            'textarea[aria-label*="query"]',
            'textarea[aria-label*="쿼리"]',
            'textarea[placeholder*="Ask"]',
            'textarea:not([disabled])'
        ];

        let blogSent = false;
        const blogPrompt = `주제 "${topic}"에 대해 소스를 기반으로 SEO 최적화된 블로그 글을 작성해주세요. 
마크다운 형식으로, 이모지를 활용하고, H1~H3 헤더를 사용하세요.
최소 1500자 이상으로 상세하게 작성해주세요.`;

        // Retry up to 5 times with increasing waits
        for (let attempt = 1; attempt <= 5 && !blogSent; attempt++) {
            console.log(`📝 Attempt ${attempt}/5 to send blog request...`);

            for (const sel of chatInputSelectors) {
                try {
                    const input = page.locator(sel).first();

                    // Check if visible
                    if (!await input.isVisible({ timeout: 3000 })) continue;

                    // Check if enabled (not disabled)
                    const isDisabled = await input.getAttribute('disabled');
                    if (isDisabled !== null) {
                        console.log(`⚠️ Chat input is disabled, waiting...`);
                        continue;
                    }

                    // Try to fill
                    await input.click();
                    await page.waitForTimeout(500);
                    await input.fill(blogPrompt);
                    await page.waitForTimeout(500);

                    // Find and click send button or press Enter
                    const sendBtn = page.locator('button[aria-label*="send"], button[aria-label*="전송"], button:has(svg), button[type="submit"]').first();
                    if (await sendBtn.isVisible({ timeout: 1000 })) {
                        await sendBtn.click();
                    } else {
                        await page.keyboard.press('Enter');
                    }

                    console.log("✅ Sent blog generation request!");
                    blogSent = true;
                    break;
                } catch (e) {
                    continue;
                }
            }

            if (!blogSent) {
                console.log(`⏳ Waiting ${attempt * 5} seconds before retry...`);
                await page.waitForTimeout(attempt * 5000);
            }
        }

        if (!blogSent) {
            console.log("⚠️ Could not auto-send blog request. Please enter manually in the browser.");
        }

        // 9. Wait for response and save
        console.log("⏳ Waiting for blog generation (60 seconds)...");
        await page.waitForTimeout(30000);

        // Try to extract the response
        const responseSelectors = [
            '[class*="response"]',
            '[class*="answer"]',
            '[class*="message"]',
            '.markdown-content'
        ];

        let blogContent = "";
        for (const sel of responseSelectors) {
            try {
                const responses = await page.locator(sel).allTextContents();
                if (responses.length > 0) {
                    blogContent = responses[responses.length - 1]; // Get last response
                    break;
                }
            } catch { continue; }
        }

        // Save output
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const outputFile = `output_deepsearch_${timestamp}.md`;

        if (blogContent) {
            fs.writeFileSync(outputFile, `# ${topic}\n\n${blogContent}`);
            console.log(`\n✅ Blog saved to: ${outputFile}`);
        } else {
            console.log("\n⚠️ Could not extract blog content automatically.");
            console.log("📋 Please copy the content manually from the browser.");
        }

        console.log("\n🎉 Deep Research workflow completed!");
        console.log("👀 Check the browser window for the generated content.");

        // Keep browser open for manual review
        console.log("\n⏳ Browser will remain open for 60 seconds for review...");
        await page.waitForTimeout(60000);

    } catch (error) {
        console.error("❌ Error:", error);
    } finally {
        await context.close();
    }
}

main().catch(console.error);
