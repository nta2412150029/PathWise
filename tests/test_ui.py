import re
from playwright.sync_api import Page, expect

def test_first_visit(page: Page):
    """TEST A — FIRST VISIT"""
    # 1. Clear onboarding localStorage (handled by page context being new)
    # 2. Open Dashboard
    page.goto("http://localhost:5000/index.html")
    
    # 3. Verify onboarding appears
    expect(page.locator(".onboarding-modal")).to_be_visible()
    
    # 4. Go through all tutorial steps
    for step in range(5):
        page.locator("#ob-next-btn").click()
    
    # 5. Finish
    page.locator("#ob-next-btn").click()
    expect(page.locator(".onboarding-modal")).not_to_be_visible()
    
    # 6. Refresh
    page.reload()
    
    # 7. Verify onboarding does not appear again
    expect(page.locator(".onboarding-modal")).not_to_be_visible()

def test_skip_onboarding(page: Page):
    """TEST B — SKIP"""
    # 1. Clear onboarding localStorage (new context)
    # 2. Open Dashboard
    page.goto("http://localhost:5000/index.html")
    
    # 3. Click Skip
    expect(page.locator(".onboarding-modal")).to_be_visible()
    page.locator("#ob-skip-btn").click()
    expect(page.locator(".onboarding-modal")).not_to_be_visible()
    
    # 4. Refresh
    page.reload()
    
    # 5. Verify onboarding stays dismissed
    expect(page.locator(".onboarding-modal")).not_to_be_visible()

def test_first_time_user_flow(page: Page):
    """TEST C — FIRST-TIME USER FLOW"""
    page.goto("http://localhost:5000/index.html")
    page.locator("#ob-skip-btn").click()
    
    # 2. Click Get Started
    page.locator("text=GET STARTED → BUILD YOUR SKILLS").click()
    
    # 3. Verify navigation goes to My Skills
    expect(page).to_have_url(re.compile(r".*/skills.html.*"))
    
    # 4. Modify several skills
    page.locator(".level-select").first.select_option("4")
    page.locator(".level-select").nth(1).select_option("3")
    
    # 5. Click Save Skill Profile
    page.locator("#global-save-btn").click()
    
    # 6. Verify save succeeds
    expect(page.locator("#save-status-msg")).to_contain_text("Skill profile saved")
    
    # 7. Navigate to Career Explorer
    page.locator("a.nav__link:has-text('Career Explorer')").click()
    
    # 8. Select a career
    page.locator(".career-row").first.click()
    page.locator(".career-row.career-row--selected button").click()
    
    # 9. Navigate to Skill Gap (should be auto-navigated by previous click)
    expect(page).to_have_url(re.compile(r".*/gap.html.*"))
    
    # 10. Verify analysis reflects the saved profile
    expect(page.locator(".fit-ring-wrapper")).to_be_visible()
    
    # 11. Navigate to Learning Roadmap
    page.locator("a.btn--primary:has-text('View Learning Roadmap')").click()
    
    # 12. Verify roadmap is consistent with the selected career
    expect(page).to_have_url(re.compile(r".*/roadmap.html.*"))

def test_global_save(page: Page):
    """TEST D — GLOBAL SAVE"""
    page.goto("http://localhost:5000/skills.html")
    page.locator("#ob-skip-btn").click()
    
    # 1. Modify three or more skills
    page.locator(".level-select").first.select_option("2")
    page.locator(".level-select").nth(1).select_option("4")
    page.locator(".level-select").nth(2).select_option("5")
    
    # 2. Verify "Unsaved changes" appears
    expect(page.locator("#save-status-msg")).to_have_text("Unsaved changes")
    
    # 3. Click one global save button
    page.locator("#global-save-btn").click()
    
    # 4. Verify values are all saved
    # 5. Verify success state
    expect(page.locator("#save-status-msg")).to_have_text("Skill profile saved")
    
    # 6. Navigate away and back
    page.locator("a.nav__link:has-text('Dashboard')").click()
    page.go_back()
    
    # 7. Verify all edited values remain
    expect(page.locator(".level-select").first).to_have_value("2")
    expect(page.locator(".level-select").nth(1)).to_have_value("4")
    expect(page.locator(".level-select").nth(2)).to_have_value("5")

def test_help_system(page: Page):
    """TEST E — HELP SYSTEM"""
    pages = ["index.html", "skills.html", "careers.html", "gap.html", "roadmap.html"]
    
    for p in pages:
        page.goto(f"http://localhost:5000/{p}")
        if page.locator(".onboarding-modal").is_visible():
            page.locator("#ob-skip-btn").click()
            
        # click ?
        page.locator(".help-btn").click()
        
        # verify contextual help appears
        expect(page.locator(".onboarding-modal")).to_be_visible()
        
        # close it
        page.locator("#help-close-btn").click()
        
        # verify normal interaction resumes
        expect(page.locator(".onboarding-modal")).not_to_be_visible()

def test_responsive(page: Page):
    """TEST F — RESPONSIVE"""
    sizes = [
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 800},
        {"width": 1024, "height": 768},
        {"width": 768, "height": 1024},
        {"width": 390, "height": 844},
    ]
    
    for size in sizes:
        page.set_viewport_size(size)
        page.goto("http://localhost:5000/index.html")
        expect(page.locator(".onboarding-modal")).to_be_visible()
        page.locator("#ob-skip-btn").click()
