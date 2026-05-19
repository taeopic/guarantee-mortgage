# Guarantee Mortgage, LLC - Mockup Site

A modern marketing site mockup for Guarantee Mortgage, a family-owned Texas mortgage broker headquartered in College Station with a second office in Mont Belvieu.

## Live Preview

https://guarantee-mortgage.surge.sh

## Stack

Static HTML, CSS, and vanilla JavaScript. No frameworks, no build step. Optimized for fast load and easy deployment to any static host.

## Structure

```
site/
  index.html                 Homepage with hero, programs, team, reviews
  about.html
  team.html                  Full team directory (13 loan officers)
  locations.html             Two offices plus 9 service cities
  reviews.html               Testimonials grid
  rates.html                 Sample wholesale rate table
  calculator.html            Live mortgage payment calculator
  contact.html               Phone, email, address, contact form
  get-started.html           Multi-field pre-approval application
  learning-center.html       Blog post grid
  loan-options/
    index.html               Program directory
    first-time-home-buyer.html
    va-home-loan.html
    fha-home-loan.html
    fixed-rate-mortgage.html
    usda-loan.html
    investment-property-loans.html
    dscr-home-loan.html
    bank-statement-program.html
    bridge-home-loan.html
    construction-home-loan.html
    reverse-mortgage.html
    seller-paid-buydown.html
    low-down-payment.html
    refinance.html
    cash-out-refinance.html
    va-loan-refinance.html
  css/styles.css
  js/main.js
  images/                    Higgsfield-generated imagery
```

## Brand

- Navy primary `#0f2545`
- Gold accent `#c9a449`
- Warm cream backgrounds `#f6f1e7`
- Display type: Fraunces
- Body: Inter
- Italic accent: Cormorant Garamond

## Business Info

- Company NMLS: 279696
- Owner: Dean Kennemer (NMLS 248739)
- College Station: 6744 Victoria Ave, College Station, TX 77845, (979) 977-3900
- Mont Belvieu: 2770 N FM 565 Rd, Mont Belvieu, TX 77523, (281) 385-5511
- Email: Team@guaranteemc.com

## Deployment

```bash
cd site
surge --domain guarantee-mortgage.surge.sh .
```
