# Requirements Document

## Introduction

CivicSense is a Zero-UI, AI-powered first-mile waste verification and logistics coordination system designed for gated communities in India. The system operates as an intelligent gatekeeper that verifies dry waste segregation quality BEFORE triggering pickup logistics, ensuring clean recycling supply chains and community-wide behavioral change.

Unlike traditional waste classification tools, CivicSense coordinates the complete civic workflow: community participants submit waste images via WhatsApp → AI verifies segregation quality →  eligible waste triggers pickup requests → drivers collect verified waste → participants earn credits → community impact is tracked. The AI acts as a critical quality control checkpoint, rejecting mixed or wet waste to maintain recycling stream integrity.

By leveraging familiar WhatsApp technology and requiring no app installation, CivicSense achieves maximum community accessibility while driving measurable improvements in source segregation compliance and first-mile recycling efficiency.

An early working prototype was implemented to validate real-world feasibility; the pilot phase will focus on community deployment evaluation and pilot-ready civic system refinement.

## Glossary

- **CivicSense_System**: The complete first-mile waste verification and logistics coordination system including WhatsApp integration, AI gatekeeper, pickup coordination, and community impact tracking
- **WhatsApp_Interface**: The conversational interface through WhatsApp that handles community participant interactions and image submissions without requiring app installation
- **AI_Gatekeeper**: The machine learning system that verifies waste segregation quality and determines pickup eligibility, acting as a quality control checkpoint before logistics activation
- **Driver_Interface**: Web-based interface for waste collection drivers to view verified pickup requests, record collected waste weights, and update pickup status
- **Pickup_Request**: Automatically generated collection request triggered only when AI verifies waste meets segregation standards
- **Green_Credits**: Point-based rewards allocated to community participants based on verified waste weight and segregation quality
- **First_Mile_Recycling**: The critical initial stage of waste collection where proper segregation at source determines recycling stream quality
- **Community_Admin**: Designated person responsible for managing community-level settings, viewing analytics, and overseeing waste management operations
- **Community_Participant**: Individual living in a gated community who submits waste for AI verification and participates in the credit-based system
- **Dry_Waste**: Non-biodegradable waste items including plastics, paper, metal, glass, and electronic waste that are eligible for recycling pickup
- **Segregation_Verification**: AI-powered process that confirms waste meets quality standards before authorizing pickup logistics
- **Community_Dashboard**: Web interface displaying community leaderboards, environmental impact metrics, and aggregated waste management analytics

## Requirements

### Requirement 1: Zero-UI WhatsApp Interaction

**User Story:** As a community participant in a gated community, I want to interact with the waste verification system exclusively through WhatsApp, so that I can participate in proper waste management without installing apps or learning new interfaces.

#### Acceptance Criteria

1. WHEN a community participant sends a message to the CivicSense WhatsApp number, THE WhatsApp_Interface SHALL respond with a welcome message and simple instructions
2. WHEN a community participant sends an image of dry waste, THE WhatsApp_Interface SHALL acknowledge receipt and initiate AI verification within 5 seconds
3. WHEN the AI verification is complete, THE WhatsApp_Interface SHALL send back eligibility results and pickup confirmation or rejection reasons
4. WHEN a community participant requests help or sends "help", THE WhatsApp_Interface SHALL provide concise usage instructions and waste category guidelines
5. THE WhatsApp_Interface SHALL support bilingual communication in English and Hindi for maximum community accessibility
6. WHEN interacting with the system, community participants SHALL complete the entire verification process in <= 2 user actions (send image + optional clarification)

### Requirement 2: AI-Gated Waste Verification and Pickup Eligibility

**User Story:** As a community participant, I want the AI system to verify my waste segregation quality and automatically trigger pickup requests only for properly segregated waste, so that I contribute to clean recycling streams and receive appropriate credits.

#### Acceptance Criteria

1. WHEN an image of dry waste is submitted, THE AI_Gatekeeper SHALL analyze segregation quality and determine pickup eligibility within 30 seconds
2. WHEN waste meets segregation standards, THE AI_Gatekeeper SHALL approve pickup and automatically generate a Pickup_Request for the driver interface, preventing contamination of public recycling streams
3. WHEN mixed waste, wet waste, or contaminated items are detected, THE AI_Gatekeeper SHALL reject the submission and provide context-aware corrective guidance
4. WHEN multiple waste items are present, THE AI_Gatekeeper SHALL verify that ALL items are properly segregated dry waste before approval, ensuring public recycling efficiency
5. Flag borderline cases for additional verification or resubmission
6. WHEN waste is rejected, THE AI_Gatekeeper SHALL explain specific issues (contamination, mixing, wet items) and provide corrective guidance to support community learning
7. THE AI_Gatekeeper SHALL maintain rejection logs to inform community education and corrective guidance programs

### Requirement 3: Logistics Orchestration and Driver Interface

**User Story:** As a waste collection driver, I want to access a prioritized list of verified pickup requests with community participant details and waste information, so that I can efficiently collect only properly segregated waste and record accurate collection data.

#### Acceptance Criteria

1. WHEN the AI_Gatekeeper approves waste submissions, THE CivicSense_System SHALL automatically create Pickup_Requests in the Driver_Interface, Pickup scheduling MAY be same-day or next scheduled collection day depending on community configuration
2. WHEN accessing the Driver_Interface, drivers SHALL see a prioritized list of verified pickups with community participant addresses, contact information, and waste descriptions
3. WHEN arriving at a pickup location, THE Driver_Interface SHALL allow drivers to confirm collection and record actual waste weight using a simple form
4. WHEN waste weight is recorded, THE CivicSense_System SHALL automatically calculate and allocate Green_Credits to the community participant based on verified weight
5. WHEN pickup is completed, THE Driver_Interface SHALL trigger automatic notification to the community participant via WhatsApp confirming collection and credits earned
6. THE Driver_Interface SHALL maintain pickup history and allow drivers to report issues (participant unavailable, waste quality problems, access issues)
7. WHEN drivers report waste quality issues at pickup, THE CivicSense_System SHALL provide additional corrective guidance and resubmission prompts

### Requirement 4: Gamification and Community Impact Tracking

**User Story:** As a community participant, I want to earn credits for properly segregated waste and see my community's collective environmental impact, so that I stay motivated to maintain good segregation practices and contribute to community sustainability goals.

#### Acceptance Criteria

1. WHEN verified waste is collected, THE CivicSense_System SHALL allocate Green_Credits to community participants based on actual collected weight (1 credit per 100g of verified dry waste) to support habit formation
2. WHEN viewing the Community_Dashboard, community participants SHALL see a community leaderboard displaying top contributors by credits earned (with privacy-preserving display names) to provide social reinforcement
3. WHEN monthly reports are generated, THE Community_Dashboard SHALL display environmental impact metrics including total waste diverted from landfills and estimated CO2 offset to build collective impact awareness
4. THE Community_Dashboard SHALL show community-wide segregation compliance rates and improvement trends over time
5. WHEN community participants achieve milestones (100, 500, 1000 credits), THE WhatsApp_Interface SHALL send achievement notifications and public recognition messages to support positive reinforcement
6. THE Community_Dashboard SHALL display "Community Champion" recognition for consistent top performers and improvement leaders to encourage community visibility
7. WHEN community admins access the dashboard, they SHALL see detailed analytics including participation rates, common rejection reasons, and community participant engagement metrics

### Requirement 5: Minimal Friction and Behavioral Change

**User Story:** As a busy community participant, I want the waste verification process to be effortless and educational, so that I can easily maintain proper segregation habits and improve my environmental impact without disrupting my daily routine.

#### Acceptance Criteria

1. WHEN a community participant sends a waste image, THE CivicSense_System SHALL provide verification results within 30 seconds using standard smartphone cameras
2. THE WhatsApp_Interface SHALL require no more than 2 user actions per complete verification cycle (image submission + optional response)
3. WHEN incorrect segregation is identified, THE WhatsApp_Interface SHALL provide context-aware corrective guidance for improvement rather than generic educational content
4. WHEN community participants show consistent improvement, THE CivicSense_System SHALL send progress visibility updates and educational feedback
5. THE WhatsApp_Interface SHALL remember community participant preferences and provide contextual quick responses based on submission history
6. WHEN community participants ask questions about specific items, THE AI_Gatekeeper SHALL provide immediate, practical answers about segregation requirements
7. THE CivicSense_System SHALL track individual behavioral change metrics and provide monthly personal impact summaries including credits earned and waste diverted

### Requirement 6: Privacy and Data Security

**User Story:** As a community participant, I want my personal information to remain private while contributing to community-level impact tracking, so that I can participate in waste management improvement without privacy concerns.

#### Acceptance Criteria

1. WHEN community participants interact with the system, THE CivicSense_System SHALL collect only data necessary for waste verification, logistics coordination, and credit allocation
2. THE CivicSense_System SHALL encrypt all image data during transmission and storage, automatically deleting images after verification completion
3. WHEN displaying community analytics, THE Community_Dashboard SHALL show only aggregated data without individual community participant identification
4. THE CivicSense_System SHALL maintain internal traceability for compliance and dispute resolution while keeping individual data private from public view
5. WHEN generating public reports, THE CivicSense_System SHALL anonymize all personal identifiers while preserving community-level insights
6. THE CivicSense_System SHALL allow community participants to view their own historical data and credits while restricting access to other participants' individual information
7. WHEN users request data deletion, THE CivicSense_System SHALL remove personal data within 7 days while preserving anonymized community analytics

### Requirement 7: System Reliability and Performance

**User Story:** As a community admin, I want the system to handle multiple concurrent users and maintain consistent performance during peak usage times, so that all community participants can access reliable waste verification and pickup services.

#### Acceptance Criteria

1. WHEN multiple community participants submit images simultaneously, THE CivicSense_System SHALL process all verification requests without degradation in 30-second response time commitment within pilot deployment constraints
2. THE CivicSense_System SHALL maintain 99% uptime during normal operating hours (6 AM to 11 PM IST) to support daily waste management routines for evaluation and demonstration purposes
3. WHEN system load increases, THE AI_Gatekeeper SHALL automatically scale to handle increased demand without affecting verification accuracy within community-scale usage
4. IF the system experiences temporary issues, THE WhatsApp_Interface SHALL inform users about delays and expected resolution times
5. THE CivicSense_System SHALL store all interaction data, pickup records, and credit transactions securely with automated backup systems
6. WHEN the Driver_Interface experiences connectivity issues, drivers SHALL be able to record pickup data offline and sync when connection is restored



### Requirement 8: Integration and Deployment

**User Story:** As a system administrator, I want to deploy and maintain the CivicSense system using cloud infrastructure, so that the system can leverage AI services, operate reliably for hackathon demonstration and support evaluation across multiple communities.

#### Acceptance Criteria

1. THE CivicSense_System SHALL integrate with WhatsApp Business API for seamless message handling and image processing without requiring mobile app installation
2. THE AI_Gatekeeper SHALL utilize cloud AI services for image recognition, waste classification, and natural language processing capabilities
3. WHEN deploying the system, THE CivicSense_System SHALL use serverless architecture for cost optimization and automatic scaling during variable usage patterns
4. THE Community_Dashboard and Driver_Interface SHALL be hosted on cloud infrastructure and accessible through standard web browsers without additional software installation
5. THE CivicSense_System SHALL implement comprehensive logging and monitoring for system health tracking, pickup success rates, and community participant engagement metrics
6. WHEN integrating with civic infrastructure, THE CivicSense_System SHALL provide APIs for future compatibility with municipal waste management systems and civic bodies
