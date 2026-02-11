
import { SharedContextManager } from "../session/shared-context-manager.js";
import { AuthManager } from "../auth/auth-manager.js";
import { BrowserSession } from "../session/browser-session.js";
import * as fs from 'fs';
import { execSync } from 'child_process';

// Force PERSISTENT profile
process.env.NOTEBOOK_PROFILE_STRATEGY = 'persistent';

// SAFETY: Kill Chrome before starting
try {
    console.log("🧹 Cleaning up old browser sessions...");
    execSync('taskkill /F /IM chrome.exe /T 2>NUL');
} catch (e) { /* Ignore */ }

async function main() {
    console.log("🚀 Starting Trends-Based Auto-Writer...");

    // Parse Arguments
    const args = process.argv.slice(2);
    const countArgIndex = args.indexOf('--count');
    const count = countArgIndex !== -1 ? parseInt(args[countArgIndex + 1], 10) : 1;

    console.log(`📊 Target: Generate ${count} blog post(s) from Google Trends Korea\n`);

    // 1. Initialize Managers
    const authManager = new AuthManager();
    const contextManager = new SharedContextManager(authManager);

    try {
        // 2. Launch Browser
        console.log("🌐 Launching browser...");
        const context = await contextManager.getOrCreateContext(true);
        const page = await context.newPage();

        // ============================================================
        // STEP 1: Fetch Trending Keywords from Google Trends RSS Feed
        // ============================================================
        console.log("📈 Fetching Google Trends Korea RSS Feed...");
        const trendingKeywords: string[] = [];

        try {
            // Use the official Google Trends RSS feed for South Korea
            const rssUrl = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR";
            await page.goto(rssUrl, { waitUntil: 'domcontentloaded' });

            // Get the raw XML content
            const content = await page.content();

            // Extract titles using regex (simple RSS parsing)
            // RSS format: <title>Keyword</title>
            const titleMatches = content.matchAll(/<title><!\[CDATA\[(.*?)\]\]><\/title>|<title>([^<]+)<\/title>/g);

            for (const match of titleMatches) {
                const title = (match[1] || match[2] || "").trim();
                // Skip the feed title itself and empty entries
                if (title &&
                    title.length > 1 &&
                    !title.includes("Daily Search Trends") &&
                    !title.includes("Google") &&
                    trendingKeywords.length < count * 2) { // Get extra in case of duplicates
                    trendingKeywords.push(title);
                }
            }

            console.log(`✅ RSS Feed parsed successfully!`);
        } catch (e) {
            console.log("⚠️ RSS fetch failed, trying backup method...");
        }

        // Fallback: If RSS failed, try the trends page directly
        if (trendingKeywords.length === 0) {
            console.log("📈 Fallback: Navigating to Google Trends Korea page...");
            await page.goto("https://trends.google.co.kr/trending?geo=KR", { waitUntil: 'domcontentloaded' });
            await page.waitForTimeout(7000); // Wait longer for dynamic content

            try {
                // Try multiple selectors for trending topics
                const selectors = [
                    '.feed-item-header', // Trending card header
                    '.trending-term-title', // Term title
                    'table a', // Links in tables
                    '[role="row"] a' // Row links
                ];

                for (const sel of selectors) {
                    if (trendingKeywords.length >= count) break;
                    try {
                        const items = await page.locator(sel).allTextContents();
                        for (const item of items) {
                            const cleaned = item.trim();
                            if (cleaned && cleaned.length > 1 && !trendingKeywords.includes(cleaned)) {
                                trendingKeywords.push(cleaned);
                            }
                        }
                    } catch { continue; }
                }
            } catch (e) {
                console.log("⚠️ Page scraping also failed.");
            }
        }

        // Final fallback: Use placeholder topics
        if (trendingKeywords.length === 0) {
            console.error("❌ Could not extract trending keywords.");
            console.log("💡 Using placeholder topics for demo...");
            trendingKeywords.push("2026 AI 트렌드", "실시간 인기 검색어", "오늘의 이슈");
        }

        console.log(`\n✅ Found ${trendingKeywords.length} trending keywords:`);
        trendingKeywords.slice(0, count).forEach((kw, i) => console.log(`   ${i + 1}. ${kw}`));
        console.log("");

        // ============================================================
        // STEP 2: For Each Keyword -> Deep Search -> NotebookLM -> Blog
        // ============================================================
        let combinedOutput = `# Trends-Based Blog Posts\nGenerated: ${new Date().toISOString()}\n\n`;

        for (let i = 0; i < Math.min(trendingKeywords.length, count); i++) {
            const keyword = trendingKeywords[i];
            console.log(`\n${"=".repeat(50)}`);
            console.log(`📝 [${i + 1}/${count}] Processing: "${keyword}"`);
            console.log("=".repeat(50));

            // --- Deep Search ---
            console.log("🔍 Deep searching for web source...");
            await page.goto(`https://www.google.com/search?q=${encodeURIComponent(keyword)}`, { waitUntil: 'domcontentloaded' });
            await page.waitForTimeout(5000);

            let sourceUrl = "";
            const searchSelectors = ['a:has(h3)', '#search .g a', '#rso a'];

            for (const sel of searchSelectors) {
                try {
                    const el = page.locator(sel).first();
                    await el.waitFor({ state: 'attached', timeout: 10000 });
                    const url = await el.getAttribute('href');
                    if (url && url.startsWith('http') && !url.includes('google.com') && !url.includes('google.co')) {
                        sourceUrl = url;
                        break;
                    }
                } catch { continue; }
            }

            if (!sourceUrl) {
                console.log("⚠️ No source URL found, skipping this topic.");
                continue;
            }
            console.log(`✅ Source URL: ${sourceUrl}`);

            // --- NotebookLM: Create Notebook & Add Source ---
            console.log("📓 Creating NotebookLM notebook...");
            await page.goto("https://notebooklm.google.com/", { waitUntil: 'domcontentloaded' });

            // Auto-fill email if login page
            try {
                const emailInput = page.locator('input[type="email"]').first();
                if (await emailInput.isVisible({ timeout: 3000 })) {
                    console.log("🔑 Auto-filling email...");
                    await emailInput.fill("tjddnn81@gmail.com");
                    await page.keyboard.press('Enter');
                    await page.waitForTimeout(5000);
                }
            } catch { /* Not on login page */ }

            // Click "New Notebook"
            try {
                const newBtn = page.locator('div[role="button"], button').filter({ hasText: /New Notebook|새 노트북/i }).first();
                await newBtn.waitFor({ state: 'visible', timeout: 60000 });
                await newBtn.click();
                console.log("✅ Created new notebook");
            } catch {
                console.log("⚠️ Could not auto-create notebook");
            }

            // Add Website Source
            try {
                console.log("🌐 Adding web source...");
                const webBtn = page.locator('div[role="button"]').filter({ hasText: /Website|Link|웹사이트/i }).first();
                await webBtn.waitFor({ state: 'visible', timeout: 30000 });
                await webBtn.click();

                const dialog = page.locator('div[role="dialog"]').first();
                await dialog.waitFor({ state: 'visible' });

                const urlInput = dialog.locator('input[type="text"], input[type="url"]').first();
                await urlInput.waitFor({ state: 'visible', timeout: 10000 });
                await urlInput.fill(sourceUrl);

                const insertBtn = dialog.locator('div[role="button"]').filter({ hasText: /Insert|Add|추가/i }).last();
                await insertBtn.click();
                console.log("✅ Added web source");

                await page.waitForTimeout(10000); // Wait for processing
            } catch (e) {
                console.log("⚠️ Could not add web source", e);
            }

            // --- Generate Blog Post ---
            console.log("✍️ Generating blog post...");
            await page.waitForURL(/notebook\//, { timeout: 30000 }).catch(() => { });

            const notebookUrl = page.url();
            const session = new BrowserSession(`trends_task_${i}`, contextManager, authManager, notebookUrl);
            await session.init();

            const prompt = `${keyword} 주제로 블로그 글을 써줘. 서론, 본론, 결론으로 나누고, 이모지와 마크다운을 사용해. 한국어로 작성해줘.`;
            const answer = await session.ask(prompt, async () => { process.stdout.write("."); });

            console.log("\n✅ Blog post generated!");

            combinedOutput += `## ${i + 1}. ${keyword}\n\n${answer}\n\n---\n\n`;
        }

        // ============================================================
        // STEP 3: Save All Posts
        // ============================================================
        const outputPath = `output_trends_${Date.now()}.md`;
        fs.writeFileSync(outputPath, combinedOutput);
        console.log(`\n${"=".repeat(50)}`);
        console.log(`🎉 SUCCESS! All ${count} blog posts saved to: ${outputPath}`);
        console.log("=".repeat(50));

    } catch (error) {
        console.error("❌ Error:", error);
    }
}

main();
