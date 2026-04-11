"""
Comprehensive Guide to Settings & Recommendations - HealthTracker
Explains how recommendations work with detailed examples
"""

import streamlit as st


def recommendations_guide_page():
    """Render the comprehensive recommendations guide page."""
    st.title("📚 Settings & Recommendations Guide")
    st.markdown("Complete guide to understanding how HealthTracker calculates your personalized targets")
    
    # Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 How It Works",
        "📊 Sample Example",
        "🔢 Calculations",
        "💡 Tips & Best Practices",
        "❓ FAQs"
    ])
    
    with tab1:
        st.header("🎯 How Settings & Recommendations Work")
        
        st.markdown("""
        ## The Complete Flow:
        
        ### Step 1️⃣: Update Your Profile & Goals
        - Enter your **current weight**, **target weight**, **age**, **height**, and **gender**
        - Choose your **activity level**, **diet preference**, and **weekly loss target**
        - These settings are saved to the database for future reference
        
        ### Step 2️⃣: System Calculates Your Targets
        Using your profile, the system calculates:
        1. **BMR** - Your metabolic rate at rest
        2. **TDEE** - Your total daily energy expenditure
        3. **Daily Calorie Intake** - What you should eat
        4. **Macro Targets** - Protein, carbs, and fat breakdown
        
        ### Step 3️⃣: You Log Your Activities
        - **Meal Logger:** Log what you eat (get calorie counts)
        - **Activity Logger:** Log workouts (get calories burned)
        - **Water Tracker:** Track hydration
        
        ### Step 4️⃣: Daily Tracking
        - System calculates your **daily deficit** based on:
          - Calories eaten - Calories burned - Deficit constant
        - Compares against your targets
        
        ### Step 5️⃣: Progress Over Time
        - **Analytics** shows your weight trend
        - **Daily Summary** shows daily performance
        - Adjust settings if needed
        """)
        
        st.divider()
        
        st.markdown("""
        ## Key Terms:
        
        | Term | Meaning | Example |
        |------|---------|---------|
        | **BMR** | Calories burned at rest | 1700 kcal/day |
        | **TDEE** | Total daily calories with activity | 2600 kcal/day |
        | **Calorie Deficit** | Difference for weight loss | 500 kcal/day |
        | **Macros** | Protein, carbs, fat breakdown | 150g, 260g, 65g |
        | **Activity Level** | How much you exercise | Moderate (3-5 days/week) |
        | **Diet Preference** | Your macro split preference | Balanced (25/50/25) |
        | **Loss Target** | Desired weekly weight loss | 0.5 kg/week |
        """)
    
    with tab2:
        st.header("📊 Sample Example - Complete Walkthrough")
        
        st.markdown("### Meet Sarah: A Complete Example")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Sarah's Profile")
            st.markdown("""
            - **Age:** 32 years
            - **Gender:** Female
            - **Height:** 165 cm
            - **Current Weight:** 85 kg
            - **Target Weight:** 70 kg
            - **Weight to Lose:** 15 kg
            """)
        
        with col2:
            st.subheader("⚙️ Sarah's Preferences")
            st.markdown("""
            - **Activity Level:** Moderate (exercises 3-4 days/week)
            - **Diet Preference:** Balanced (normal macro split)
            - **Weekly Loss Target:** 0.5 kg/week
            - **Timeline:** ~30 weeks to goal
            """)
        
        st.divider()
        
        st.subheader("🔢 System Calculations for Sarah:")
        
        calc_col1, calc_col2 = st.columns(2)
        
        with calc_col1:
            st.info("""
            **Step 1: Calculate BMR**
            Using Mifflin-St Jeor equation:
            - BMR = (10 × 85) + (6.25 × 165) - (5 × 32) - 161
            - BMR = 850 + 1031.25 - 160 - 161
            - BMR = **1560 kcal/day**
            
            *(This is what Sarah burns just existing)*
            """)
            
            st.info("""
            **Step 2: Calculate TDEE**
            Using activity multiplier (moderate = 1.55):
            - TDEE = BMR × 1.55
            - TDEE = 1560 × 1.55
            - TDEE = **2418 kcal/day**
            
            *(Sarah burns this with her current activity level)*
            """)
        
        with calc_col2:
            st.info("""
            **Step 3: Calculate Daily Deficit**
            For 0.5 kg/week loss:
            - 1 kg of fat = 7700 calories
            - Daily deficit = (0.5 × 7700) / 7
            - Daily deficit = **550 kcal/day**
            
            *(Sarah needs a 550 kcal deficit to lose 0.5kg/week)*
            """)
            
            st.info("""
            **Step 4: Calculate Daily Calorie Intake**
            - Daily Intake = TDEE - Deficit
            - Daily Intake = 2418 - 550
            - Daily Intake = **1868 kcal/day**
            
            *(This is what Sarah should eat daily)*
            """)
            
            st.info("""
            **Step 5: Calculate Exercise Calories to Burn**
            - Exercise Calories = TDEE - BMR
            - Exercise Calories = 2418 - 1560
            - Exercise Calories = **858 kcal/day**
            
            *(This is what Sarah should burn through exercise and activities)*
            *(OR she can rely on diet if she can't exercise)*
            """)
        
        st.divider()
        
        st.subheader("🥗 Sarah's Macro Targets:")
        
        macro_col1, macro_col2, macro_col3 = st.columns(3)
        
        with macro_col1:
            st.metric("Protein", "117g", "25% of 1868 kcal")
            st.caption("4 cal/g × 117g = 468 cal")
        
        with macro_col2:
            st.metric("Carbs", "234g", "50% of 1868 kcal")
            st.caption("4 cal/g × 234g = 936 cal")
        
        with macro_col3:
            st.metric("Fat", "52g", "25% of 1868 kcal")
            st.caption("9 cal/g × 52g = 468 cal")
        
        st.info("**Total:** 468 + 936 + 468 = 1868 kcal ✅")
        
        st.divider()
        
        st.subheader("🔥 Sarah's Exercise Target:")
        
        exercise_col1, exercise_col2 = st.columns(2)
        
        with exercise_col1:
            st.metric("Exercise Calories Target", "858 kcal/day", "TDEE - BMR")
            st.caption("Through gym, running, sports, or daily activities")
        
        with exercise_col2:
            st.metric("Daily Deficit Required", "550 kcal/day", "For 0.5 kg/week loss")
            st.caption("Can be achieved through diet, exercise, or both")
        
        st.divider()
        
        st.subheader("📅 Sarah's Daily Action Plan:")
        
        st.markdown("""
        **Daily Target: 1868 kcal eat | 858 kcal burn (exercise) | 550 kcal deficit**
        
        **Macros: 117g protein - 234g carbs - 52g fat - 27g fiber**
        
        """)
        
        st.divider()
        
        st.subheader("📊 Sarah's Projected Progress:")
        
        progress_data = {
            "Week": [0, 4, 8, 12, 16, 20, 24, 30],
            "Weight (kg)": [85, 83, 81, 79, 77, 75, 73, 70],
            "Total Lost": [0, 2, 4, 6, 8, 10, 12, 15],
            "Loss/Week": [0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        }
        
        import pandas as pd
        df = pd.DataFrame(progress_data)
        
        st.dataframe(df, width='stretch', hide_index=True)
        
        st.success("""
        **Sarah's Journey:**
        At 0.5 kg/week loss, Sarah will reach her 70 kg goal in approximately **30 weeks** (7 months)
        """)
    
    with tab3:
        st.header("🔢 Detailed Calculation Formulas")
        
        st.subheader("1. BMR Calculation (Mifflin-St Jeor Equation)")
        st.markdown("""
        #### For Men:
        ```
        BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
        ```
        
        #### For Women:
        ```
        BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161
        ```
        
        **Science:** This formula is most accurate for calculating basal metabolic rate
        """)
        
        st.subheader("2. TDEE Calculation")
        st.markdown("""
        #### Formula:
        ```
        TDEE = BMR × Activity Multiplier
        ```
        
        #### Activity Multipliers:
        - **Sedentary:** 1.2 (minimal exercise)
        - **Light:** 1.375 (1-3 days/week)
        - **Moderate:** 1.55 (3-5 days/week)
        - **Very Active:** 1.725 (6-7 days/week)
        - **Extremely Active:** 1.9 (physical job or 2x training/day)
        """)
        
        st.subheader("2b. Exercise Calories Calculation")
        st.markdown("""
        #### Formula:
        ```
        Exercise Calories = TDEE - BMR
        ```
        
        This represents the calories burned through daily activities and intentional exercise.
        
        #### Example:
        ```
        If BMR = 1560 kcal and TDEE = 2418 kcal
        Then Exercise Calories = 2418 - 1560 = 858 kcal/day
        ```
        
        **This is your daily exercise/activity burn target.**
        """)
        
        st.subheader("3. Daily Calorie Intake for Weight Loss")
        st.markdown("""
        #### Formula:
        ```
        Daily Deficit = (Target_kg_per_week × 7700) / 7
        Daily Intake = TDEE - Daily Deficit
        Minimum = 1200 kcal (safety limit)
        ```
        
        #### Example for 0.5 kg/week loss:
        ```
        Daily Deficit = (0.5 × 7700) / 7 = 550 kcal
        Daily Intake = 2600 - 550 = 2050 kcal
        ```
        
        **Note:** 1 kg of body fat = 7700 calories (scientific consensus)
        """)
        
        st.subheader("4. Macro Target Calculation")
        st.markdown("""
        #### By Diet Type:
        
        **Balanced:** 25% Protein, 50% Carbs, 25% Fat
        ```
        Protein = (calories × 0.25) / 4
        Carbs = (calories × 0.50) / 4
        Fat = (calories × 0.25) / 9
        ```
        
        **High Protein:** 35% Protein, 40% Carbs, 25% Fat
        ```
        Protein = (calories × 0.35) / 4
        Carbs = (calories × 0.40) / 4
        Fat = (calories × 0.25) / 9
        ```
        
        **Low Carb:** 30% Protein, 25% Carbs, 45% Fat
        ```
        Protein = (calories × 0.30) / 4
        Carbs = (calories × 0.25) / 4
        Fat = (calories × 0.45) / 9
        ```
        
        **Vegetarian:** 20% Protein, 50% Carbs, 30% Fat
        ```
        Protein = (calories × 0.20) / 4
        Carbs = (calories × 0.50) / 4
        Fat = (calories × 0.30) / 9
        ```
        
        #### Calorie Conversion:
        - 1g Protein = 4 calories
        - 1g Carbs = 4 calories
        - 1g Fat = 9 calories
        """)
        
        st.subheader("5. Daily Net Deficit (for tracking)")
        st.markdown("""
        #### Formula:
        ```
        Daily Net Deficit = Calories Eaten - Calories Burned - Deficit Constant
        ```
        
        #### Interpretation:
        - **Positive number:** Surplus (gained a little)
        - **Negative number:** Deficit (lost a little)
        - **-550 kcal:** Perfect deficit for 0.5 kg/week loss
        
        #### Example:
        ```
        Ate: 1800 kcal
        Burned: 600 kcal (exercise + BMR)
        Deficit Constant: 550 kcal
        
        Daily Net = 1800 - 600 - 550 = -650 kcal
        (Better than target! -650 instead of -550)
        ```
        """)
    
    with tab4:
        st.header("💡 Tips & Best Practices")
        
        st.subheader("✅ DO:")
        st.markdown("""
        1. **Start with Moderate settings** - 0.5 kg/week loss is sustainable
        2. **Log consistently** - Track meals and exercise accurately
        3. **Combine diet & exercise** - Much better than one alone
        4. **Adjust gradually** - If not losing weight, reduce calories by 100-200
        5. **Eat enough protein** - Helps preserve muscle during weight loss
        6. **Stay hydrated** - Drink water regularly (tracked in Water Tracker)
        7. **Get strength training** - Builds muscle, increases BMR
        8. **Sleep well** - Better sleep aids weight loss
        9. **Review weekly** - Check your progress, adjust if needed
        10. **Be patient** - Steady progress beats rapid loss
        """)
        
        st.subheader("❌ DON'T:")
        st.markdown("""
        1. **Aim for >1 kg/week loss** - Too aggressive, hard to sustain
        2. **Eat below 1200 kcal** - Can harm metabolism
        3. **Rely on diet alone** - Exercise adds many benefits
        4. **Skip meals** - Leads to overeating later
        5. **Blame daily fluctuations** - Weight varies by 1-2 kg (water, food)
        6. **Cut all carbs/fat** - You need both for health
        7. **Ignore hunger signals** - If very hungry, increase calories
        8. **Expect linear progress** - Weight loss varies week to week
        9. **Change settings weekly** - Give it 2-3 weeks to see results
        10. **Compare with others** - Everyone's targets are different
        """)
        
        st.subheader("🎯 Optimization Tips:")
        
        tips_col1, tips_col2 = st.columns(2)
        
        with tips_col1:
            st.info("""
            **For Better Adherence:**
            - Start with **0.5 kg/week** (easiest to maintain)
            - Choose diet preference you enjoy
            - Log meals while you eat (not later)
            - Set phone reminders for meals
            """)
        
        with tips_col2:
            st.info("""
            **For Faster Progress:**
            - Add strength training (3x/week minimum)
            - Increase daily steps (10,000+ target)
            - Eat high protein (preserves muscle)
            - Track macros carefully
            """)
        
        st.subheader("📈 When to Adjust Settings:")
        
        st.markdown("""
        **After 3-4 weeks, if no progress:**
        1. Verify you're logging correctly (use scale for portions)
        2. Reduce daily calories by 100-200 kcal
        3. Increase exercise (especially strength training)
        4. Check if deficit constant is realistic
        
        **If feeling unwell:**
        1. Increase calories by 100-200
        2. Check you're eating enough protein
        3. Ensure hydration (3L water/day minimum)
        4. Consider consulting a nutritionist
        
        **If weight loss stalls (plateau):**
        1. This is normal after 4-6 weeks
        2. Your metabolism adapts
        3. Change your exercise routine
        4. Reduce calories slightly or increase exercise
        """)
    
    with tab5:
        st.header("❓ Frequently Asked Questions")
        
        with st.expander("❓ How often should I update my recommendations?", expanded=False):
            st.markdown("""
            **Answer:** After every major weight change (5+ kg loss/gain), OR every 3 months.
            
            - Weight loss changes your BMR
            - Updated BMR should recalculate your targets
            - Update your "Current Weight" in Profile & Goals
            - Your recommendations will automatically recalculate
            """)
        
        with st.expander("❓ What if I'm not losing weight?", expanded=False):
            st.markdown("""
            **Check in this order:**
            
            1. **Logging accuracy** - Are you measuring portions correctly?
            2. **Calorie count** - Are you eating the target amount?
            3. **Consistency** - Is this over 3+ weeks?
            4. **Activity level** - Have you been exercising?
            5. **Water weight** - Weight fluctuates 1-2 kg normally
            
            **Solution:** If truly not losing after 3 weeks + accurate logging:
            - Reduce calories by 100-200
            - Increase exercise by 30 minutes
            - See a doctor (thyroid issues?)
            """)
        
        with st.expander("❓ Can I change my settings anytime?", expanded=False):
            st.markdown("""
            **Answer:** Yes, but here's the recommendation:
            
            - **Activity Level:** Change if your exercise routine changes significantly
            - **Diet Preference:** Change if you want different macros (doesn't affect calories)
            - **Weekly Loss Target:** Change after 2-3 weeks if current pace is too hard/easy
            
            💡 Avoid changing settings weekly - give each setting time to show results
            """)
        
        with st.expander("❓ What's the difference between BMR and TDEE?", expanded=False):
            st.markdown("""
            | Aspect | BMR | TDEE |
            |--------|-----|------|
            | **What** | Calories at rest | Calories with activity |
            | **Example** | 1600 kcal | 2500 kcal |
            | **Usage** | Baseline for TDEE | Your daily burn |
            | **How** | Scientific formula | BMR × Activity multiplier |
            | **What affects it** | Genetics, age, weight | Activity level |
            
            **Simple analogy:**
            - BMR = Your car's idle speed
            - TDEE = Your car's speed when driving
            """)
        
        with st.expander("❓ How accurate are these calculations?", expanded=False):
            st.markdown("""
            **Accuracy Level: ~90%**
            
            These are population-average formulas:
            - Works well for most people
            - Individual variation: ±10-15%
            - Best verified with real-world tracking
            
            **If your results differ:**
            - Track for 2-3 weeks accurately
            - See if weight loss matches predictions
            - Adjust your deficit constant up/down by 100-200
            
            Example: If you're losing twice as fast as expected, increase daily calories by 200
            """)
        
        with st.expander("❓ What about muscle vs fat loss?", expanded=False):
            st.markdown("""
            **To preserve muscle while losing fat:**
            
            1. **Eat enough protein** - 1.6-2.2g per kg body weight
            2. **Strength training** - 3+ days per week (with weights)
            3. **Don't lose too fast** - 0.5-0.75 kg/week maximum
            4. **Stay hydrated** - Critical for muscle function
            
            **Example for 85 kg person:**
            - Minimum protein: 85 × 1.6 = **136g/day**
            - Recommended: 85 × 2.0 = **170g/day**
            
            Our Balanced diet gives you adequate protein for this.
            """)
        
        with st.expander("❓ Can I go below 1200 kcal?", expanded=False):
            st.markdown("""
            **Answer: NO (without medical supervision)**
            
            1200 kcal is the legal/health minimum because:
            - Not enough nutrients for vital functions
            - Damages metabolism
            - Causes muscle loss
            - Leads to nutritional deficiencies
            - Often results in binge eating
            
            **If you can't eat that much:**
            - Increase exercise instead of cutting calories
            - Choose high-volume, low-calorie foods (vegetables)
            - See a nutritionist
            """)


if __name__ == "__main__":
    recommendations_guide_page()
