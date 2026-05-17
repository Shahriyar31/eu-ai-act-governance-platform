EU_AI_ACT_CHUNKS = [
    {
        "id": "article_5",
        "title": "Article 5 — Prohibited AI Practices",
        "content": """The EU AI Act prohibits certain AI practices entirely under Article 5. 
        These include: AI systems that deploy subliminal techniques to manipulate human behaviour 
        causing harm; systems that exploit vulnerabilities of specific groups; social scoring 
        systems by public authorities; real-time remote biometric identification in public spaces 
        by law enforcement (with narrow exceptions); AI systems for emotion recognition in 
        workplaces or educational institutions; biometric categorisation inferring sensitive 
        attributes; and mass surveillance systems. These systems are banned and cannot be 
        placed on the EU market regardless of safeguards applied."""
    },
    {
        "id": "article_6",
        "title": "Article 6 — Classification of High Risk AI Systems",
        "content": """Article 6 defines High Risk AI systems as those listed in Annex III 
        of the EU AI Act. High Risk AI systems include systems used in: biometric identification 
        and categorisation; management of critical infrastructure; education and vocational 
        training; employment and worker management; access to essential services; law enforcement; 
        migration and border control; administration of justice; and democratic processes. 
        Systems that are safety components of products regulated under EU harmonisation 
        legislation are also High Risk."""
    },
    {
        "id": "article_9",
        "title": "Article 9 — Risk Management System",
        "content": """High Risk AI systems must implement a risk management system under 
        Article 9. This system must be a continuous iterative process running throughout 
        the entire lifecycle. It must identify and analyse known and foreseeable risks, 
        estimate and evaluate risks that may emerge during use, evaluate risks based on 
        post-market monitoring data, and adopt risk mitigation measures. Residual risks 
        must be judged acceptable. The risk management system must be documented and 
        updated regularly."""
    },
    {
        "id": "article_10",
        "title": "Article 10 — Data and Data Governance",
        "content": """High Risk AI systems must comply with data governance requirements 
        under Article 10. Training, validation, and testing datasets must be relevant, 
        representative, free of errors, and complete. Data governance practices must cover 
        data collection, data preparation, examination for biases, and identification of 
        data gaps. Special category personal data may only be used for bias monitoring 
        under strict conditions. Data must be managed with appropriate data governance 
        policies throughout the AI lifecycle."""
    },
    {
        "id": "article_11",
        "title": "Article 11 — Technical Documentation",
        "content": """Providers of High Risk AI systems must draw up technical documentation 
        before placing the system on the market under Article 11. Documentation must include: 
        general description of the system and its intended purpose; description of system 
        components and development process; information on training methodologies and datasets; 
        validation and testing procedures; risk management documentation; cybersecurity measures; 
        and performance metrics. Documentation must be kept up to date and made available 
        to national authorities on request."""
    },
    {
        "id": "article_12",
        "title": "Article 12 — Record Keeping and Logging",
        "content": """High Risk AI systems must have automatic logging capabilities under 
        Article 12. Logs must enable monitoring of system operation throughout its lifetime. 
        Logging must capture events relevant for identifying risks and substantial modifications. 
        For systems used by public authorities in law enforcement or migration, logs must 
        be retained for a minimum of six months. Logs must be available to relevant authorities 
        for post-market monitoring and investigations."""
    },
    {
        "id": "article_13",
        "title": "Article 13 — Transparency and Information Provision",
        "content": """High Risk AI systems must be sufficiently transparent under Article 13. 
        Providers must ensure systems are accompanied by instructions for use that enable 
        deployers to interpret outputs and use the system appropriately. Information must 
        include: identity and contact details of the provider; system capabilities and 
        limitations; performance metrics and known biases; human oversight measures; 
        computational resource requirements; and expected lifetime. AI-generated content 
        must be clearly labelled."""
    },
    {
        "id": "article_14",
        "title": "Article 14 — Human Oversight",
        "content": """High Risk AI systems must be designed to enable human oversight under 
        Article 14. Systems must allow natural persons to fully understand system capabilities 
        and limitations, monitor operation, detect anomalies and malfunctions, and override 
        or interrupt system operation. Deployers must assign human oversight to persons with 
        necessary competence and authority. For systems making decisions affecting individuals, 
        humans must be able to intervene before decisions take effect. Oversight measures 
        must be proportionate to risks involved."""
    },
    {
        "id": "article_15",
        "title": "Article 15 — Accuracy, Robustness and Cybersecurity",
        "content": """High Risk AI systems must achieve appropriate levels of accuracy, 
        robustness, and cybersecurity under Article 15. Accuracy levels must be declared 
        in accompanying documentation. Systems must be resilient to errors, faults, and 
        inconsistencies. Systems must be protected against attempts by unauthorised third 
        parties to alter use or performance. Technical redundancy solutions and fail-safe 
        plans must be implemented. Systems must be tested against adversarial attacks 
        relevant to their intended use context."""
    },
    {
        "id": "article_16",
        "title": "Article 16 — EU Database Registration",
        "content": """Providers of High Risk AI systems must register their systems in the 
        EU AI Act public database before placing them on the market under Article 16. 
        Registration must include system name and version, provider identity and contact 
        details, intended purpose and deployment context, risk management summary, 
        conformity assessment details, and post-market monitoring plan. Registration 
        must be updated when significant changes are made. Public authorities using 
        High Risk AI must also register as deployers."""
    },
    {
        "id": "article_50",
        "title": "Article 50 — Transparency for Limited Risk AI",
        "content": """AI systems that interact directly with humans must meet transparency 
        obligations under Article 50. Providers must ensure systems are designed so that 
        natural persons are informed they are interacting with an AI system. This applies 
        to chatbots and conversational AI. AI-generated synthetic content including 
        deepfakes must be labelled. Emotion recognition systems and biometric categorisation 
        must inform persons subjected to them. These obligations apply even for Limited Risk 
        systems that are not classified as High Risk."""
    },
    {
        "id": "gdpr_article_35",
        "title": "GDPR Article 35 — Data Protection Impact Assessment",
        "content": """A Data Protection Impact Assessment is required under GDPR Article 35 
        when processing is likely to result in high risk to individuals. DPIA is mandatory 
        when using systematic and extensive automated processing including profiling that 
        produces legal or similarly significant effects; processing of special category data 
        at large scale; and systematic monitoring of publicly accessible areas at large scale. 
        For High Risk AI systems that process personal data, a DPIA is almost always required. 
        The DPIA must describe processing, assess necessity, identify risks, and define 
        mitigation measures."""
    },
    {
        "id": "annex_3",
        "title": "Annex III — High Risk AI Use Cases",
        "content": """Annex III of the EU AI Act lists specific High Risk AI use cases. 
        In healthcare: AI for diagnosis, treatment decisions, and medical device operation. 
        In employment: CV screening, interview analysis, promotion decisions, and task 
        allocation monitoring. In education: student assessment, exam proctoring, and 
        admission decisions. In law enforcement: crime prediction, evidence evaluation, 
        and lie detection. In border control: risk assessment of persons and document 
        verification. In justice: legal research assistance and court decision support. 
        In finance: credit scoring and insurance risk assessment affecting individuals."""
    },
    {
        "id": "conformity_assessment",
        "title": "Conformity Assessment and CE Marking",
        "content": """High Risk AI systems must undergo conformity assessment before market 
        placement. For most High Risk AI systems, providers conduct self-assessment against 
        harmonised standards. For biometric identification and law enforcement systems, 
        third-party assessment by a notified body is required. Successful assessment leads 
        to CE marking, which is mandatory for placing High Risk AI on the EU market. 
        The conformity assessment must be repeated when significant modifications are made 
        to the system. Declarations of conformity must be kept for ten years."""
    },
    {
        "id": "post_market",
        "title": "Post-Market Monitoring and Incident Reporting",
        "content": """Providers of High Risk AI systems must establish post-market monitoring 
        systems. Monitoring must actively collect and analyse data on system performance 
        throughout its lifetime. Serious incidents — defined as incidents causing death, 
        serious harm, or significant property damage — must be reported to national 
        supervisory authorities without undue delay. Malfunctions that could breach 
        fundamental rights must also be reported. Market surveillance authorities have 
        powers to request access to training data, source code, and system documentation."""
    },
    {
        "id": "nist_govern",
        "title": "NIST AI RMF — Govern Function",
        "content": """The NIST AI Risk Management Framework Govern function establishes 
        organisational practices for AI risk management. It requires organisations to 
        establish policies, processes, and accountability structures for AI risk. 
        Key activities include defining AI risk tolerance, assigning roles and responsibilities, 
        establishing organisational culture of AI safety, ensuring workforce competency, 
        and maintaining transparency with stakeholders. Governance structures must be 
        documented and reviewed regularly. The Govern function underpins all other 
        NIST AI RMF functions."""
    },
    {
        "id": "nist_map",
        "title": "NIST AI RMF — Map Function",
        "content": """The NIST AI RMF Map function identifies and categorises AI risks 
        in context. Activities include defining the AI system's intended purpose and 
        deployment context, identifying stakeholders and their interests, cataloguing 
        AI risks specific to the system and use case, assessing business value against 
        risk, and prioritising risks for treatment. Mapping must consider bias and 
        fairness risks, privacy risks, security risks, and operational risks. 
        Context-specific risks must be documented and reassessed when deployment 
        context changes."""
    },
    {
        "id": "nist_measure",
        "title": "NIST AI RMF — Measure Function",
        "content": """The NIST AI RMF Measure function analyses and assesses AI risks 
        quantitatively and qualitatively. Activities include testing AI systems for 
        performance against defined metrics, evaluating bias and fairness across 
        demographic groups, assessing robustness and adversarial vulnerability, 
        measuring privacy risk, and tracking risk treatment effectiveness. Measurement 
        approaches must be appropriate to the AI system type and risk level. Results 
        must be documented and communicated to relevant stakeholders."""
    },
    {
        "id": "nist_manage",
        "title": "NIST AI RMF — Manage Function",
        "content": """The NIST AI RMF Manage function implements risk treatment plans 
        and responds to AI incidents. Activities include prioritising and implementing 
        risk mitigations, monitoring residual risks, responding to AI incidents and 
        near-misses, maintaining incident response plans, and communicating risk status 
        to leadership. Risk treatment options include risk avoidance, mitigation, 
        transfer, and acceptance. Residual risks must be formally accepted by 
        accountable personnel. Lessons learned from incidents must be incorporated 
        into risk management practices."""
    },
    {
        "id": "owasp_llm",
        "title": "OWASP LLM Top 10 — Key Risks",
        "content": """The OWASP LLM Top 10 identifies the most critical security risks 
        for Large Language Model applications. LLM01 Prompt Injection: malicious inputs 
        manipulating model behaviour. LLM02 Insecure Output Handling: failing to validate 
        LLM outputs before use. LLM03 Training Data Poisoning: compromising training data 
        integrity. LLM06 Sensitive Information Disclosure: LLMs revealing confidential data. 
        LLM08 Excessive Agency: LLMs taking harmful autonomous actions. LLM09 Overreliance: 
        treating LLM outputs as authoritative without verification. These risks require 
        input validation, output sanitisation, access controls, and human oversight."""
    }
]