# Cross-skill boundary decisions

## Design versus application engineering

Visual hierarchy, interaction behavior, accessibility in the rendered experience, and brand expression belong to `interface-design`. Component contracts, data flow, server/client boundaries, API integration, and persistence belong to `application-engineering`. Use both only when the task genuinely spans both layers.

## Application engineering versus software delivery

Architecture answers “what should this system be?” Delivery answers “how do we safely change and prove it?” Framework expertise must not weaken the delivery skill's evidence requirements; process ceremony must not replace an engineering decision.

## Documents versus interface design

The document skill owns file-format fidelity, editable structure, calculations, pagination, and rendering. The interface skill contributes visual direction when appearance is material. A slide deck is not treated as a web page, and a PDF is not validated only by inspecting its source representation.

## Agent orchestration versus ordinary parallel work

Agent orchestration applies when capability boundaries, tool contracts, handoffs, or context isolation must be designed. Ordinary independent implementation steps may still run concurrently under `software-delivery` without turning the task into an agent-architecture exercise.

## Reasoning modes versus domain authority

A requested interaction mode changes how a problem is explored or communicated. It does not override safety, project instructions, evidence standards, or domain-specific workflows. The mode ends when the user changes it or when applying it would misrepresent certainty.

## Systems operation versus security assessment

Routine shell and operating-system work does not imply permission to scan, exploit, or broaden security scope. Security assessment activates only when explicitly requested and remains bounded to the named systems and authorization.

## Marketing strategy versus interface and artifact production

`marketing-and-growth` owns the audience, offer, channel, pricing, conversion hypothesis, and commercial measurement. `interface-design` owns visual and interaction direction; `document-productivity` owns office-artifact fidelity. They may compose, but a persuasive objective does not give marketing rules authority over accessibility, factual integrity, or file-format correctness.

## Connected-service operation versus integration design

`connected-service-automation` operates an already connected service for a user, with explicit account, target, authority, and verification. `application-engineering` implements product integrations; `agent-tooling-and-orchestration` designs reusable tool interfaces. A one-off external action should not silently expand into connector development, and a connector implementation should not be treated as permission to mutate user data.

## Data science versus application engineering

`data-science-and-ml` owns data-generating assumptions, statistical validity, learned-model behavior, training, evaluation, and monitoring. `application-engineering` owns the surrounding service and product architecture. Use both when a model becomes a product component, while keeping model-quality evidence distinct from API reliability and product impact.
