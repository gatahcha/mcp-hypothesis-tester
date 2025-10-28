# Hypothesis Testing Explained Simply
## Using the Sales Example

---

## The Basic Idea

**Hypothesis testing is like a court trial:**
- 🏛️ You start by assuming someone is **innocent** (not guilty)
- 🔍 You look for **evidence** to prove they're guilty
- ⚖️ If evidence is **strong enough**, you declare them guilty
- If evidence is **weak**, they remain innocent

**In statistics:**
- 🛒 You start by assuming sales are **normal** (unchanged from baseline)
- 📊 You collect data to see if sales **actually changed**
- 📈 If the difference is **large enough** (unlikely by chance), you declare sales changed
- If difference is **small** (could just be random), sales are probably unchanged

---

## Your Sales Example Explained

### **The Situation**
- Historical average: **$5,000 per day** (this is what you expect)
- Current quarter average: **$5,150 per day** (what you actually measured)
- Difference: **+$150** (that's interesting, but did it really increase?)
- Question: **Is this increase real or just luck?**

---

## The Null Hypothesis (H₀)

### **What is H₀?**
The **null hypothesis** is your "starting assumption" — **the boring, default claim**.

**In your case:**
```
H₀: μ = 5000

This means: "Store sales are still $5,000 on average.
The $150 increase we see is just random noise/luck,
not a real change."
```

### **Why is it called "null"?**
Because it means "no effect, no change, nothing special happened."

### **Real-World Translation:**
🛒 "Boss, sales look higher, but I'm betting it's just because:
- We got lucky this quarter
- Had some random big-spending customers
- It's normal monthly variation
- Nothing fundamentally changed"

---

## The Alternative Hypothesis (H₁ or Ha)

### **What is H₁?**
The **alternative hypothesis** is what you're trying to **prove**. It's the opposite of the null.

**In your case:**
```
H₁: μ ≠ 5000

This means: "Store sales are NOT $5,000 on average anymore.
The $150 increase is REAL, something actually changed."
```

### **Real-World Translation:**
📈 "Boss, I think sales actually increased! The $150 difference is not just luck—something real happened (better marketing, new customers, better service, etc.)."

---

## The Two Competing Claims

```
┌─────────────────────────────────────┬──────────────────────────────────────┐
│  Null Hypothesis (H₀)               │  Alternative Hypothesis (H₁)         │
├─────────────────────────────────────┼──────────────────────────────────────┤
│  "Nothing changed"                  │  "Something changed"                 │
│  Sales = $5,000 (same as before)    │  Sales ≠ $5,000 (different)          │
│  The +$150 is just random luck      │  The +$150 is real, not luck         │
│  Like: Not guilty                   │  Like: Guilty                        │
│  Default assumption                 │  What we're trying to prove          │
└─────────────────────────────────────┴──────────────────────────────────────┘
```

---

## The Statistical Test (T-Test)

### **What are we actually doing?**

We're asking: **"How likely is it that we'd see +$150 difference if nothing actually changed?"**

### **The Calculation Explained**

```
t = (observed mean - hypothesized mean) / (standard deviation / √n)

t = (5150 - 5000) / (480 / √45)

t = 150 / 71.55

t = 2.096
```

### **Breaking this down:**

1. **Numerator (150):** How big is the difference?
   - We observed $5,150
   - Expected $5,000
   - Difference = $150 (pretty big!)

2. **Denominator (71.55):** How much noise is there?
   - Sales vary by SD = $480 each day
   - With 45 days of data, noise reduces to 480/√45 ≈ 71.55
   - (More data = less noise)

3. **Result (2.096):** The signal-to-noise ratio
   - Is the signal (difference) loud compared to noise?
   - 2.096 means: difference is **2 times larger than the noise**

---

## P-Value: The Key Decision Point

### **What is a P-Value?**

**P-value = "Probability that we'd see this if H₀ is true"**

In plain English:
```
"If sales really ARE $5,000 (H₀ is true),
what's the chance we'd randomly observe $5,150?"
```

### **In Your Case:**

Your t-statistic is **2.096**

↓

P-value ≈ **0.042** (approximately 4.2%)

### **What does this mean?**

```
"If store sales truly average $5,000 (nothing changed),
there's only a 4.2% chance we'd randomly see $5,150 average
in a sample of 45 days."
```

**Translation:** Pretty unlikely! But possible.

---

## The Decision Rule

### **The Magic Threshold: α = 0.05**

Scientists agreed on a **significance level** of **5%** (0.05).

```
If P-value < 0.05  →  "This is too unlikely to be random"
                       → REJECT H₀ (declare H₁ true)
                       → We declare the change is REAL

If P-value ≥ 0.05  →  "This could easily be random"
                       → FAIL TO REJECT H₀
                       → We cannot declare the change is real
```

### **Why 5%?**
It's arbitrary, but agreed upon. It balances:
- Not being too strict (missing real changes)
- Not being too loose (seeing changes that don't exist)

---

## Your Specific Case: Decision

### **The Numbers**
- t = 2.096
- p-value ≈ 0.042
- Threshold = 0.05

### **The Comparison**
```
P-value (0.042) < Threshold (0.05)?

YES! ✅ 0.042 < 0.05
```

### **The Decision**
```
✅ REJECT H₀
```

### **What does this mean?**

❌ We REJECT: "Sales are still $5,000" (H₀)

✅ We ACCEPT: "Sales have actually changed" (H₁)

### **Business Conclusion**
```
"Your current quarter sales of $5,150 is significantly 
different from the historical $5,000. This is NOT just 
random noise—something real happened! Your sales improved."
```

---

## The Four Possible Outcomes

### **What could happen?**

```
                    TRUTH IN REALITY
                  ┌──────────┬──────────┐
                  │ H₀ TRUE  │ H₁ TRUE  │
            ┌─────┼──────────┼──────────┤
            │ Reject │ Type I  │ Correct  │
    OUR     │ H₀   │ Error   │ (Good!)  │
    DECISION│     │(False   │          │
            │     │Positive)│          │
            ├─────┼──────────┼──────────┤
            │Fail  │ Correct │ Type II  │
            │to    │ (Good!) │ Error    │
            │reject│         │(False    │
            │ H₀   │         │Negative) │
            └─────┴──────────┴──────────┘
```

#### **Type I Error (False Positive)** 🚨
- We say sales increased, but they didn't
- Like: Innocent person declared guilty
- Controlled by significance level (α = 0.05)
- 5% chance of this happening

#### **Type II Error (False Negative)** 😴
- We say sales didn't change, but they did
- Like: Guilty person declared innocent
- More common with small sample sizes

---

## Let's Try Another Example to Cement This

### **Coffee Shop Example**

**Claim:** "A new espresso machine makes better coffee"

**Null Hypothesis (H₀):** "The new machine makes coffee the same as before"
```
μ_old = μ_new (no real difference)
```

**Alternative Hypothesis (H₁):** "The new machine makes coffee differently"
```
μ_old ≠ μ_new (there IS a difference)
```

**We collect data:**
- 30 customers rated old machine: avg = 7.2/10
- 30 customers rated new machine: avg = 7.8/10
- Difference = 0.6 points
- P-value = 0.03

**Decision:**
```
P-value (0.03) < 0.05? YES!

REJECT H₀ ✅

Conclusion: "The new machine makes coffee significantly 
differently! Customers like it better."
```

---

## Common Misconceptions (AVOID THESE!)

### ❌ **WRONG:** "P-value is the probability that H₀ is true"
**CORRECT:** "P-value is the probability of seeing this data IF H₀ is true"

### ❌ **WRONG:** "P-value < 0.05 means it's definitely different"
**CORRECT:** "P-value < 0.05 means it's unlikely to happen by chance, so we believe it's real"

### ❌ **WRONG:** "We accept H₀ if P > 0.05"
**CORRECT:** "We fail to reject H₀" (subtle but important difference)

### ❌ **WRONG:** "We choose H₀ and H₁ based on the data"
**CORRECT:** "We choose H₀ and H₁ BEFORE looking at data (they should be your research question)"

---

## The Logic Flow (Remember This!)

```
1. START: Assume H₀ is true
   ↓
2. COLLECT: Gather data
   ↓
3. CALCULATE: Compute test statistic (t-value)
   ↓
4. FIND: Calculate P-value
   ↓
5. COMPARE: Is P-value < 0.05?
   ↓
   YES → REJECT H₀, Accept H₁ (Change is real!)
   NO  → FAIL TO REJECT H₀ (Not enough evidence to prove change)
```

---

## Your Sales Case: Complete Walkthrough

### **Step 1: Set Up Hypotheses** (before looking at data!)
```
H₀: μ = 5000  (sales haven't changed)
H₁: μ ≠ 5000  (sales have changed)
```

### **Step 2: Collect Data**
```
n = 45 days
mean = $5,150
SD = $480
```

### **Step 3: Calculate T-Test**
```
t = (5150 - 5000) / (480 / √45)
t = 150 / 71.55
t = 2.096
```

### **Step 4: Find P-Value**
```
Using t-table or software: P-value ≈ 0.042
```

### **Step 5: Make Decision**
```
0.042 < 0.05? YES!

REJECT H₀ ✅
```

### **Step 6: Communicate to Boss**
```
"Sales of $5,150 are significantly higher than our 
historical $5,000 baseline (p = 0.042). This represents 
a real increase, not just random variation. We should 
investigate what drove this improvement!"
```

---

## Real-World Interpretation

### **What you tell executives:**

✅ **GOOD:** "We're 95% confident that sales have genuinely increased. There's only a 5% chance this is just luck."

❌ **BAD:** "The p-value is 0.042."

✅ **GOOD:** "With our current sales of $5,150 vs. baseline of $5,000, the probability of seeing this difference by chance (if nothing changed) is only 4.2%. So something real happened!"

❌ **BAD:** "We reject the null hypothesis."

---

## Quick Reference Card

| Concept | Meaning |
|---------|---------|
| **H₀ (Null)** | "Nothing changed" — default assumption |
| **H₁ (Alt)** | "Something changed" — what we try to prove |
| **P-value** | "Chance of seeing this if H₀ is true" |
| **α (Alpha)** | Significance level (usually 0.05 or 5%) |
| **t-statistic** | Signal strength / Noise ratio |
| **Reject H₀** | Evidence is strong enough to declare change |
| **Fail to reject H₀** | Evidence is NOT strong enough |

---

## Practice Problems

### **Problem 1:** Coffee Shop
- Historical: customers = 100/day
- Last week: 120/day average
- Measured p-value = 0.08

**What do you conclude?**
```
Answer: 0.08 > 0.05
Fail to reject H₀
"We don't have strong enough evidence that daily customers increased.
The 20 extra customers could just be random fluctuation."
```

### **Problem 2:** Website Redesign
- Old site: avg time = 5 minutes
- New site: avg time = 5.5 minutes
- Measured p-value = 0.02

**What do you conclude?**
```
Answer: 0.02 < 0.05
Reject H₀
"The new website causes significantly different (longer) visit times.
This is real, not just luck!"
```

---

## The Bottom Line

**Think of it like this:**

You're a detective investigating whether something changed.

1. **Start:** "Nothing happened" (H₀)
2. **Gather clues:** Collect data
3. **Evaluate clues:** Calculate p-value
4. **Decision:** "Is there enough evidence to convict?" (p < 0.05?)
5. **Verdict:** "Guilty!" (Reject H₀) or "Not enough evidence" (Fail to reject)

In your sales case:
- The evidence (p = 0.042) is strong enough
- You declare: "Sales genuinely increased!"
- You can act on this (invest more, celebrate, etc.)

---

## Key Takeaways

✅ **H₀ is always "nothing changed"** — the boring default  
✅ **H₁ is what you're trying to prove** — the exciting alternative  
✅ **P-value tells you likelihood** — if H₀ were true, how likely is your data?  
✅ **p < 0.05 is the magic threshold** — data is "significant"  
✅ **Reject H₀ means** — we believe H₁ is true instead  
✅ **Always set H₀ & H₁ BEFORE looking at data** — no cheating!

---

**Congratulations! You now understand the basics of hypothesis testing!** 🎉

This same logic applies to all 26 tests in your guide—they just use different formulas, but the principle is always the same.

