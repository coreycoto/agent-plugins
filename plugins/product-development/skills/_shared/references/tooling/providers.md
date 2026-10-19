# Vendor-owned platform guidance

Use the provider's installed specialist skill or plugin when a task needs its
APIs, SDK patterns or deployment procedure. Inspect the skills actually exposed
by the current host and read the relevant procedure; a marketplace declaration
or a link below does not establish installation, authentication or task access.

| Platform and task | Official guidance |
| --- | --- |
| Clerk authentication, organizations, sessions, webhooks or framework integration | [Clerk Skills](https://clerk.com/docs/guides/ai/skills), including the `clerk` router and task-specific skills from [clerk/skills](https://github.com/clerk/skills) |
| Stripe integration, billing, payments or account inspection | [Stripe agent skills](https://docs.stripe.com/skills) and [agent plugins](https://docs.stripe.com/agents/plugin) |
| Cloudflare Workers, storage, AI, networking or security | [Cloudflare agent guidance](https://developers.cloudflare.com/docs-for-agents/) and [Cloudflare Skills](https://github.com/cloudflare/skills) |

If a specialist is unavailable, use the linked official documentation and report
the capability gap. Installing a dependency or connecting a provider is a
separate setup action. For an authorized installation, qualify the vendor source,
selected skill paths and exact revision or package version through the consumer's
installation workflow; verify acquired content and fresh-session discovery.
Do not run a vendor quickstart merely to check availability, copy vendor skill
implementations into this plugin, or assume a shared name establishes provenance.

The consumer owns selected versions, credentials, account and environment
identities, and application-specific integration policy. Personal installations
can be declared in dotfiles; repository and cloud provisioning select their own
dependencies. These references supply task routing rather than implicit plugin
dependencies or automatic restoration.

For actual operations, verify the intended Clerk instance/organization, Stripe
account and sandbox versus live context, or Cloudflare account/zone/Worker and
environment. Follow the consumer's authorized action and provider workflow.
Preserve executable denials across shell and connector choices; installing a
specialist does not grant permission to provision, deploy or mutate business data.

Bun runtime and dependency selection is covered by [runtimes](runtimes.md).
[Service tools](services.md) covers browser, Turbo, Vercel and Neon tool selection;
prefer available vendor procedures for their detailed implementation guidance too.
