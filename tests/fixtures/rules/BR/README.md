# BR rule fixtures

Generated from Biosafety and biosecurity rules for T-405.

- BR-01: Every construct MUST be routed through a configured screening adaptor (IGSC v3.0 / IBBIS Common Mechanism / SecureDNA / institutional blacklist).
- BR-02: A hit result from the screening adaptor MUST block ordering and route the construct to a designated reviewer (institutional biosafety officer / IBC).
- BR-03: A watchlist result MUST require explicit reviewer sign-off, recorded in provenance, before ordering.
- BR-04: The screening verdict MUST be persisted in the construct's metadata with timestamp and adaptor version.
- BR-05: Constructs containing any sequence from a Select Agent / pathogen on the HHS / USDA Select Agent list MUST trigger an automatic block regardless of screening verdict.
- BR-06: Constructs intended for in-vivo use, environmental release, or clinical-grade manufacturing MUST also undergo a stricter NIH Guidelines section IIIA/IIIB classification pass.
- BR-07: The user MUST declare biosafety tier at design time; the system MUST refuse to compile if tier is unset.
- BR-08: Replication-competent viral vectors MUST be explicitly justified, flagged, and require dual sign-off.
- BR-09: The user MUST declare whether the construct uses any Risk Group 2+ organism component; if yes, dual sign-off required.
- BR-10: The full biosafety / screening trail MUST be exportable as an audit document for institutional review.
- BR-11: engine.sop_protocol MUST NOT render an operational wet-lab protocol unless the user's administrator-granted AuthorisationProfile covers (a) the construct's biosafety tier, (b) the construct's host classes, (c) the construct's assembly chemistry, (d) the construct's downstream-use class, and the user's UserDeclaration (SOP library, biosafety approval ID, role-of-operation) lies inside the granted profile. Self-declaration by a User role MUST NOT lift this gate.
- BR-12: Authorisation-profile mutation MUST require AdminPrincipal or DeveloperBootstrapPrincipal credentials and MUST emit an AdminActionMinted / Modified / Revoked event to the immutable audit log. User and Reviewer roles MUST NOT mutate any AuthorisationProfile.
- BR-13: Tampered or expired AuthorisationProfile records MUST be rejected by the engine on load; integrity is enforced by institutional signature.
- BR-14: The BlockOperationalProtocol gate MUST fire whenever the construct's RiskAdvisoryReport contains an advisory of severity caution or strong_caution that has not been explicitly acknowledged by a signed RiskAdvisoryAcknowledgement whose report_content_hash and construct_checksum match the current versions. Passive UI dismissal MUST NOT satisfy this requirement. Declines and escalations route the construct to alternative workflows but do NOT unblock authorisation on their own.
