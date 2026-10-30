## Privacy Policy

_Last updated: 25 October 2026_

Paydar ("the app", "we") is a subscription tracker that runs on your device. This policy explains what data the app handles and who it is shared with. By using Paydar you agree to this policy.

### The short version

- Paydar has **no account and no servers of its own**. The subscriptions, payment method labels, reminders and settings you enter are stored **on your device** and, if you use iCloud, backed up to **your own private iCloud**. We never receive, see, or store them.
- The app connects to the internet to **download currency exchange rates**, to **download a public list of subscription price changes** and to **check your Paydar Pro purchase**. Purchases are processed by **Apple** and validated by **RevenueCat**, as described below.
- From version 1.2.0 Paydar shows **no ads** and does not track you. Earlier versions showed ads (see "Advertising in versions before 1.2.0").

### Data stored on your device

Everything you create in Paydar (your subscriptions, prices, billing dates, payment-method names, notes, reminder preferences and chosen currency) is saved in local storage on your device. It is not transmitted to us and is not stored on any Paydar server. If you export a CSV or backup file, it stays wherever you choose to save or share it.

**iCloud backup.** If you are signed in to iCloud, Paydar automatically keeps a backup copy of this data in your private iCloud (Apple's iCloud key-value storage), so you can restore it after reinstalling the app or on a new iPhone. This copy is stored by Apple under your Apple ID and can only be read by Paydar on devices signed in to your Apple ID. We have no access to it.

**Deleting your data.** **Settings → Delete all data** removes your data from this device. From version 1.1.9 it also clears the iCloud backup copy; in earlier versions that copy stays in your private iCloud. Uninstalling the app removes the copy on your device.

### Currency exchange rates

To convert prices into your base currency, the app periodically fetches public exchange-rate data from third-party providers (currently `open.er-api.com` and a jsDelivr-hosted dataset). These are anonymous requests for rate data. They do **not** include your subscriptions or any personal information.

### Subscription price changes

To tell you when a service you track changes its price, the app downloads a public list of announced price changes from our website (`interactivemedia91-arch.github.io`, hosted on GitHub Pages) each time you open it. This is the same file for everyone. The match against your subscriptions happens on your device, and the request does **not** include your subscriptions or any personal information. Like any website, GitHub receives your IP address when the file is downloaded. Paydar never changes a price by itself: it asks you first.

### Advertising in versions before 1.2.0 (Google AdMob)

Paydar has no ads from version 1.2.0. Earlier versions showed ads through **Google AdMob**; this section applies only if you still use one of them. To serve and measure ads, Google and its partners may collect and process information such as your device's advertising identifier, IP address, general device information and app-usage signals.

- **Tracking permission (iOS).** Paydar asks once whether you allow tracking. If you allow it, Google may use your device's advertising identifier to show ads that are more relevant to you. If you don't, Paydar requests **non-personalized ads** only. You can change this at any time in **Settings → Privacy & Security → Tracking**.
- **EEA, UK and Switzerland.** Before any ads load, Paydar shows Google's consent form so you can choose how your data is used for advertising.

This data is handled under Google's policies, not ours:

- Google Privacy Policy: https://policies.google.com/privacy
- How Google uses information from apps that use its services: https://policies.google.com/technologies/partner-sites

Updating to version 1.2.0 or later removes all ads.

### Purchases (Apple App Store & RevenueCat)

The optional one-time Paydar Pro purchase (and the earlier ad-free upgrade) is processed by **Apple's App Store** (in-app purchase). We use **RevenueCat** to validate and remember it so your Pro status works across reinstalls. RevenueCat receives the purchase/transaction details and an anonymous app-user identifier (versions before 1.2.0 also sent your tracking-permission status, allowed or not); it does not receive your subscription data. See RevenueCat's privacy policy: https://www.revenuecat.com/privacy/. We never receive or store your payment card details; those are handled entirely by Apple.

### Notifications

Renewal and trial reminders are scheduled **locally** on your device. Paydar does not use push servers and does not send your data anywhere to deliver them.

### Children

Paydar is not directed to children under 13 and we do not knowingly collect data from them.

### Changes to this policy

We may update this policy as the app evolves. Material changes will be reflected by updating the date at the top of this section.

### Contact

Questions about privacy or the app? Email **interactivemedia91@gmail.com**.

