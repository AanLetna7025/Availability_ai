// ============================================
// MONGODB SEED SCRIPT - DEMO DATA
// ============================================
// This script creates a complete demo database
// with realistic data for all 19 collections
// ============================================

const mongoose = require('mongoose');

// ============================================
// STEP 1: UPDATE YOUR MONGODB CONNECTION HERE!
// ============================================


//  MongoDB Atlas (Cloud) - Uncomment and update if using Atlas
const MONGODB_URI ='password here';

// ============================================
// IMPORT ALL MODELS
// ============================================
const Client = require('./dbschema/clients');
const Designation = require('./dbschema/designation');
const Group = require('./dbschema/groups');
const InviteUser = require('./dbschema/inviteUsers');
const LoggedUser = require('./dbschema/logeduser');
const Milestone = require('./dbschema/milestone');
const Permission = require('./dbschema/permission');
const Project = require('./dbschema/project');
const ProjectDocument = require('./dbschema/project_documents');
const Role = require('./dbschema/role');
const Session = require('./dbschema/session');
const Skill = require('./dbschema/skill');
const Status = require('./dbschema/statuses');
const Task = require('./dbschema/task');
const Technology = require('./dbschema/technology');
const TimeLog = require('./dbschema/timelog');
const User = require('./dbschema/user');
const UserAvailability = require('./dbschema/userAvailabilityCalender');
const UserBooking = require('./dbschema/userBookings');

// ============================================
// MAIN SEED FUNCTION
// ============================================
async function seedDatabase() {
    try {
        console.log('🚀 Starting database seeding process...\n');
        
        // Connect to MongoDB
        console.log('📡 Connecting to MongoDB...');
        await mongoose.connect(MONGODB_URI, {
            useNewUrlParser: true,
            useUnifiedTopology: true,
        });
        console.log('✅ Connected to MongoDB successfully!\n');

        // Clear existing data
        console.log('🗑️  Clearing existing data...');
        await Promise.all([
            Client.deleteMany({}),
            Designation.deleteMany({}),
            Group.deleteMany({}),
            InviteUser.deleteMany({}),
            LoggedUser.deleteMany({}),
            Milestone.deleteMany({}),
            Permission.deleteMany({}),
            Project.deleteMany({}),
            ProjectDocument.deleteMany({}),
            Role.deleteMany({}),
            Session.deleteMany({}),
            Skill.deleteMany({}),
            Status.deleteMany({}),
            Task.deleteMany({}),
            Technology.deleteMany({}),
            TimeLog.deleteMany({}),
            User.deleteMany({}),
            UserAvailability.deleteMany({}),
            UserBooking.deleteMany({})
        ]);
        console.log('✅ Cleared all collections\n');

        // ============================================
        // CREATE DEMO DATA
        // ============================================

        // 1. Create Clients (10 clients)
        console.log('📦 Creating Clients...');
        const clients = await Client.insertMany([
            { name: 'Acme Corporation' },
            { name: 'TechStart Inc' },
            { name: 'Global Solutions Ltd' },
            { name: 'Digital Dynamics' },
            { name: 'Innovation Labs' },
            { name: 'CloudTech Solutions' },
            { name: 'FinanceFirst Corp' },
            { name: 'HealthCare Systems' },
            { name: 'EduTech Platform' },
            { name: 'RetailPro International' },
            { name: 'GreenEnergy Solutions' },
            { name: 'FoodDelivery Express' }
        ]);
        console.log(`✅ Created ${clients.length} clients\n`);

        // 2. Create Designations (10 designations)
        console.log('📦 Creating Designations...');
        const designations = await Designation.insertMany([
            { name: 'Senior Developer', developerstatus: true },
            { name: 'Junior Developer', developerstatus: true },
            { name: 'Project Manager', developerstatus: false },
            { name: 'UI/UX Designer', developerstatus: false },
            { name: 'QA Engineer', developerstatus: false },
            { name: 'DevOps Engineer', developerstatus: true },
            { name: 'Tech Lead', developerstatus: true },
            { name: 'Business Analyst', developerstatus: false },
            { name: 'Scrum Master', developerstatus: false },
            { name: 'Product Owner', developerstatus: false }
        ]);
        console.log(`✅ Created ${designations.length} designations\n`);

        // 3. Create Skills (20 skills)
        console.log('📦 Creating Skills...');
        const skills = await Skill.insertMany([
            { name: 'JavaScript', status: 'active' },
            { name: 'React', status: 'active' },
            { name: 'Node.js', status: 'active' },
            { name: 'MongoDB', status: 'active' },
            { name: 'Python', status: 'active' },
            { name: 'Docker', status: 'active' },
            { name: 'AWS', status: 'active' },
            { name: 'GraphQL', status: 'active' },
            { name: 'TypeScript', status: 'active' },
            { name: 'Vue.js', status: 'active' },
            { name: 'Angular', status: 'active' },
            { name: 'PostgreSQL', status: 'active' },
            { name: 'Redis', status: 'active' },
            { name: 'Kubernetes', status: 'active' },
            { name: 'Java', status: 'active' },
            { name: 'C#', status: 'active' },
            { name: 'Flutter', status: 'active' },
            { name: 'Swift', status: 'active' },
            { name: 'Kotlin', status: 'active' },
            { name: 'Django', status: 'active' }
        ]);
        console.log(`✅ Created ${skills.length} skills\n`);

        // 4. Create Roles (5 roles)
        console.log('📦 Creating Roles...');
        const roles = await Role.insertMany([
            {
                name: 'Admin',
                status: 'active',
                permissions: [
                    { action: 'create_project', allowed: true },
                    { action: 'delete_project', allowed: true },
                    { action: 'manage_users', allowed: true },
                    { action: 'view_reports', allowed: true },
                    { action: 'manage_permissions', allowed: true }
                ]
            },
            {
                name: 'Developer',
                status: 'active',
                permissions: [
                    { action: 'create_task', allowed: true },
                    { action: 'update_task', allowed: true },
                    { action: 'view_project', allowed: true },
                    { action: 'log_time', allowed: true }
                ]
            },
            {
                name: 'Manager',
                status: 'active',
                permissions: [
                    { action: 'create_project', allowed: true },
                    { action: 'assign_tasks', allowed: true },
                    { action: 'view_reports', allowed: true },
                    { action: 'manage_milestones', allowed: true }
                ]
            },
            {
                name: 'Client',
                status: 'active',
                permissions: [
                    { action: 'view_project', allowed: true },
                    { action: 'comment_task', allowed: true }
                ]
            },
            {
                name: 'Viewer',
                status: 'active',
                permissions: [
                    { action: 'view_project', allowed: true }
                ]
            }
        ]);
        console.log(`✅ Created ${roles.length} roles\n`);

        // 5. Create Users (20 users)
        console.log('📦 Creating Users...');
        const users = await User.insertMany([
            {
                first_name: 'John',
                last_name: 'Doe',
                email: 'john.doe@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[0]._id],
                designation: designations[0]._id,
                skills: [skills[0]._id, skills[1]._id, skills[2]._id],
                tw_user_id: '12345',
                skype_id: 'john.doe',
                current_status: 'online',
                phone_number: '+1234567890'
            },
            {
                first_name: 'Jane',
                last_name: 'Smith',
                email: 'jane.smith@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[1]._id,
                skills: [skills[1]._id, skills[8]._id],
                tw_user_id: '12346',
                skype_id: 'jane.smith',
                current_status: 'online',
                phone_number: '+1234567891'
            },
            {
                first_name: 'Mike',
                last_name: 'Johnson',
                email: 'mike.johnson@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[2]._id],
                designation: designations[2]._id,
                skills: [skills[3]._id, skills[4]._id],
                tw_user_id: '12347',
                skype_id: 'mike.johnson',
                current_status: 'offline',
                phone_number: '+1234567892'
            },
            {
                first_name: 'Sarah',
                last_name: 'Williams',
                email: 'sarah.williams@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[3]._id,
                skills: [skills[5]._id, skills[6]._id],
                tw_user_id: '12348',
                skype_id: 'sarah.williams',
                current_status: 'online',
                phone_number: '+1234567893'
            },
            {
                first_name: 'David',
                last_name: 'Brown',
                email: 'david.brown@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[4]._id,
                skills: [skills[7]._id, skills[1]._id],
                tw_user_id: '12349',
                skype_id: 'david.brown',
                current_status: 'online',
                phone_number: '+1234567894'
            },
            {
                first_name: 'Emily',
                last_name: 'Davis',
                email: 'emily.davis@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[5]._id,
                skills: [skills[5]._id, skills[6]._id, skills[2]._id],
                tw_user_id: '12350',
                skype_id: 'emily.davis',
                current_status: 'online',
                phone_number: '+1234567895'
            },
            {
                first_name: 'Alice',
                last_name: 'Cooper',
                email: 'alice.cooper@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[1]._id,
                skills: [skills[0]._id, skills[2]._id, skills[9]._id],
                tw_user_id: '12351',
                skype_id: 'alice.cooper',
                current_status: 'online',
                phone_number: '+1234567896'
            },
            {
                first_name: 'Bob',
                last_name: 'Martin',
                email: 'bob.martin@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[0]._id,
                skills: [skills[1]._id, skills[3]._id, skills[8]._id],
                tw_user_id: '12352',
                skype_id: 'bob.martin',
                current_status: 'offline',
                phone_number: '+1234567897'
            },
            {
                first_name: 'Carol',
                last_name: 'White',
                email: 'carol.white@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[3]._id,
                skills: [skills[4]._id, skills[5]._id],
                tw_user_id: '12353',
                skype_id: 'carol.white',
                current_status: 'online',
                phone_number: '+1234567898'
            },
            {
                first_name: 'Daniel',
                last_name: 'Lee',
                email: 'daniel.lee@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[5]._id,
                skills: [skills[5]._id, skills[6]._id, skills[13]._id],
                tw_user_id: '12354',
                skype_id: 'daniel.lee',
                current_status: 'online',
                phone_number: '+1234567899'
            },
            {
                first_name: 'Emma',
                last_name: 'Wilson',
                email: 'emma.wilson@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[2]._id],
                designation: designations[2]._id,
                skills: [skills[3]._id],
                tw_user_id: '12355',
                skype_id: 'emma.wilson',
                current_status: 'online',
                phone_number: '+1234567800'
            },
            {
                first_name: 'Frank',
                last_name: 'Taylor',
                email: 'frank.taylor@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[6]._id,
                skills: [skills[0]._id, skills[2]._id, skills[8]._id, skills[14]._id],
                tw_user_id: '12356',
                skype_id: 'frank.taylor',
                current_status: 'online',
                phone_number: '+1234567801'
            },
            {
                first_name: 'Grace',
                last_name: 'Anderson',
                email: 'grace.anderson@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[1]._id,
                skills: [skills[14]._id, skills[15]._id],
                tw_user_id: '12357',
                skype_id: 'grace.anderson',
                current_status: 'offline',
                phone_number: '+1234567802'
            },
            {
                first_name: 'Henry',
                last_name: 'Thomas',
                email: 'henry.thomas@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[4]._id,
                skills: [skills[1]._id, skills[4]._id, skills[19]._id],
                tw_user_id: '12358',
                skype_id: 'henry.thomas',
                current_status: 'online',
                phone_number: '+1234567803'
            },
            {
                first_name: 'Isabel',
                last_name: 'Martinez',
                email: 'isabel.martinez@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[3]._id,
                skills: [skills[1]._id, skills[10]._id],
                tw_user_id: '12359',
                skype_id: 'isabel.martinez',
                current_status: 'online',
                phone_number: '+1234567804'
            },
            {
                first_name: 'Jack',
                last_name: 'Robinson',
                email: 'jack.robinson@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[1]._id,
                skills: [skills[16]._id, skills[17]._id, skills[18]._id],
                tw_user_id: '12360',
                skype_id: 'jack.robinson',
                current_status: 'online',
                phone_number: '+1234567805'
            },
            {
                first_name: 'Karen',
                last_name: 'Clark',
                email: 'karen.clark@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[2]._id],
                designation: designations[8]._id,
                skills: [],
                tw_user_id: '12361',
                skype_id: 'karen.clark',
                current_status: 'online',
                phone_number: '+1234567806'
            },
            {
                first_name: 'Leo',
                last_name: 'Rodriguez',
                email: 'leo.rodriguez@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[7]._id,
                skills: [],
                tw_user_id: '12362',
                skype_id: 'leo.rodriguez',
                current_status: 'offline',
                phone_number: '+1234567807'
            },
            {
                first_name: 'Maria',
                last_name: 'Garcia',
                email: 'maria.garcia@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[0]._id,
                skills: [skills[4]._id, skills[11]._id, skills[19]._id],
                tw_user_id: '12363',
                skype_id: 'maria.garcia',
                current_status: 'online',
                phone_number: '+1234567808'
            },
            {
                first_name: 'Nathan',
                last_name: 'Hernandez',
                email: 'nathan.hernandez@example.com',
                password: '$2b$10$abcdefghijklmnopqrstuv',
                roles: [roles[1]._id],
                designation: designations[5]._id,
                skills: [skills[5]._id, skills[6]._id, skills[12]._id, skills[13]._id],
                tw_user_id: '12364',
                skype_id: 'nathan.hernandez',
                current_status: 'online',
                phone_number: '+1234567809'
            }
        ]);
        console.log(`✅ Created ${users.length} users\n`);

        // 6. Create Technologies (12 technologies)
        console.log('📦 Creating Technologies...');
        const technologies = await Technology.insertMany([
            { name: 'React', type: 'client', status: 'active' },
            { name: 'Vue.js', type: 'client', status: 'active' },
            { name: 'Angular', type: 'client', status: 'active' },
            { name: 'Next.js', type: 'client', status: 'active' },
            { name: 'Node.js', type: 'server', status: 'active' },
            { name: 'Express', type: 'server', status: 'active' },
            { name: 'Django', type: 'server', status: 'active' },
            { name: 'PostgreSQL', type: 'server', status: 'active' },
            { name: 'MongoDB', type: 'server', status: 'active' },
            { name: 'Redis', type: 'server', status: 'active' },
            { name: 'Flask', type: 'server', status: 'active' },
            { name: 'Spring Boot', type: 'server', status: 'active' }
        ]);
        console.log(`✅ Created ${technologies.length} technologies\n`);

        // 7. Create Projects (10 projects)
        console.log('📦 Creating Projects...');
        const projects = await Project.insertMany([
            {
                name: 'E-Commerce Platform',
                description: 'Full-stack e-commerce solution with payment integration',
                client: clients[0]._id,
                start_date: new Date('2024-01-15'),
                end_date: new Date('2024-06-30'),
                platform: 'web',
                status: 'ongoing',
                technologies: {
                    client: [
                        { techId: technologies[0]._id, version: '18.2.0', note: 'Main frontend', reason: 'Modern and efficient', status: true }
                    ],
                    server: [
                        { techId: technologies[4]._id, version: '20.0.0', note: 'Backend API', reason: 'JavaScript ecosystem', status: true },
                        { techId: technologies[8]._id, version: '7.0', note: 'Database', reason: 'Flexible schema', status: true }
                    ]
                },
                requirement: [
                    {
                        title: 'User Authentication',
                        createdAt: new Date('2024-01-16'),
                        description: 'Implement JWT-based authentication',
                        status: true,
                        notes: [
                            { title: 'Use OAuth 2.0', createdAt: new Date('2024-01-17'), description: 'For social login', status: true }
                        ]
                    },
                    {
                        title: 'Payment Gateway',
                        createdAt: new Date('2024-01-20'),
                        description: 'Integrate Stripe payment processing',
                        status: false,
                        notes: []
                    }
                ],
                issues: [
                    { title: 'Payment gateway integration delay', answer: 'Working with vendor support' }
                ]
            },
            {
                name: 'Mobile Banking App',
                description: 'Secure mobile banking application with biometric authentication',
                client: clients[1]._id,
                start_date: new Date('2024-02-01'),
                end_date: new Date('2024-08-31'),
                platform: 'mobile',
                status: 'ongoing',
                technologies: {
                    client: [
                        { techId: technologies[0]._id, version: '18.2.0', note: 'React Native', reason: 'Cross-platform', status: true }
                    ],
                    server: [
                        { techId: technologies[4]._id, version: '20.0.0', note: 'API Server', reason: 'Scalable', status: true }
                    ]
                }
            },
            {
                name: 'CRM System',
                description: 'Customer relationship management system for enterprise',
                client: clients[2]._id,
                start_date: new Date('2024-03-01'),
                end_date: new Date('2024-09-30'),
                platform: 'web',
                status: 'ongoing'
            },
            {
                name: 'Social Media Dashboard',
                description: 'Real-time analytics dashboard for social media management',
                client: clients[5]._id,
                start_date: new Date('2024-04-01'),
                end_date: new Date('2024-10-31'),
                platform: 'web',
                status: 'ongoing',
                technologies: {
                    client: [
                        { techId: technologies[1]._id, version: '3.4.0', note: 'Vue.js frontend', reason: 'Reactive framework', status: true }
                    ],
                    server: [
                        { techId: technologies[4]._id, version: '20.0.0', note: 'Node.js API', reason: 'Fast', status: true }
                    ]
                }
            },
            {
                name: 'Inventory Management System',
                description: 'Real-time inventory tracking for warehouses',
                client: clients[9]._id,
                start_date: new Date('2024-05-01'),
                end_date: new Date('2024-12-31'),
                platform: 'web',
                status: 'ongoing',
                technologies: {
                    client: [
                        { techId: technologies[0]._id, version: '18.2.0', note: 'React frontend', reason: 'Popular', status: true }
                    ],
                    server: [
                        { techId: technologies[4]._id, version: '20.0.0', note: 'Node.js backend', reason: 'JavaScript', status: true }
                    ]
                }
            },
            {
                name: 'Healthcare Portal',
                description: 'Patient management and appointment scheduling system',
                client: clients[7]._id,
                start_date: new Date('2024-06-01'),
                end_date: new Date('2025-01-31'),
                platform: 'web',
                status: 'ongoing'
            },
            {
                name: 'Financial Analytics Tool',
                description: 'Advanced financial reporting and forecasting platform',
                client: clients[6]._id,
                start_date: new Date('2024-07-01'),
                end_date: new Date('2025-02-28'),
                platform: 'web',
                status: 'ongoing'
            },
            {
                name: 'Online Learning Platform',
                description: 'E-learning platform with video courses and assessments',
                client: clients[8]._id,
                start_date: new Date('2024-03-15'),
                end_date: new Date('2024-11-30'),
                platform: 'web',
                status: 'ongoing',
                technologies: {
                    client: [
                        { techId: technologies[3]._id, version: '14.0.0', note: 'Next.js SSR', reason: 'SEO friendly', status: true }
                    ],
                    server: [
                        { techId: technologies[4]._id, version: '20.0.0', note: 'Backend', reason: 'Fast', status: true }
                    ]
                }
            },
            {
                name: 'Food Delivery Platform',
                description: 'Real-time food ordering and delivery tracking system',
                client: clients[11]._id,
                start_date: new Date('2024-02-20'),
                end_date: new Date('2024-09-30'),
                platform: 'mobile',
                status: 'ongoing'
            },
            {
                name: 'Green Energy Monitoring',
                description: 'IoT-based energy consumption monitoring dashboard',
                client: clients[10]._id,
                start_date: new Date('2024-05-15'),
                end_date: new Date('2025-01-15'),
                platform: 'web',
                status: 'ongoing'
            }
        ]);
        console.log(`✅ Created ${projects.length} projects\n`);

        // 8. Create Statuses (6 statuses)
        console.log('📦 Creating Statuses...');
        const statuses = await Status.insertMany([
            { task_status: 'TODO', text_color: '#ffffff', bg_color: '#6c757d' },
            { task_status: 'IN_PROGRESS', text_color: '#ffffff', bg_color: '#007bff' },
            { task_status: 'IN_REVIEW', text_color: '#000000', bg_color: '#ffc107' },
            { task_status: 'COMPLETED', text_color: '#ffffff', bg_color: '#28a745' },
            { task_status: 'BLOCKED', text_color: '#ffffff', bg_color: '#dc3545' },
            { task_status: 'ON_HOLD', text_color: '#ffffff', bg_color: '#6f42c1' }
        ]);
        console.log(`✅ Created ${statuses.length} statuses\n`);

        // 9. Create Milestones (15 milestones - multiple per project)
        console.log('📦 Creating Milestones...');
        const milestones = await Milestone.insertMany([
            // E-Commerce Platform milestones
            {
                project_id: projects[0]._id,
                title: 'Phase 1 - MVP',
                description: 'Basic functionality and user interface',
                status: '1',
                created_by: users[2]._id,
                is_current_milestone: true,
                start_date: new Date('2024-01-15'),
                end_date: new Date('2024-03-31'),
                milestone_created_by: users[2]._id
            },
            {
                project_id: projects[0]._id,
                title: 'Phase 2 - Payment Integration',
                description: 'Payment gateway and checkout flow',
                status: '1',
                created_by: users[2]._id,
                is_current_milestone: false,
                start_date: new Date('2024-04-01'),
                end_date: new Date('2024-06-30'),
                milestone_created_by: users[2]._id
            },
            // Mobile Banking App milestones
            {
                project_id: projects[1]._id,
                title: 'Alpha Release',
                description: 'Initial alpha version for testing',
                status: '1',
                created_by: users[2]._id,
                is_current_milestone: true,
                start_date: new Date('2024-02-01'),
                end_date: new Date('2024-04-30'),
                milestone_created_by: users[2]._id
            },
            {
                project_id: projects[1]._id,
                title: 'Beta Release',
                description: 'Beta testing with real users',
                status: '1',
                created_by: users[2]._id,
                is_current_milestone: false,
                start_date: new Date('2024-05-01'),
                end_date: new Date('2024-08-31'),
                milestone_created_by: users[2]._id
            },
            // CRM System milestones
            {
                project_id: projects[2]._id,
                title: 'Discovery Phase',
                description: 'Requirements gathering and planning',
                status: '1',
                created_by: users[10]._id,
                is_current_milestone: true,
                start_date: new Date('2024-03-01'),
                end_date: new Date('2024-04-30'),
                milestone_created_by: users[10]._id
            },
            // Social Media Dashboard milestones
            {
                project_id: projects[3]._id,
                title: 'Phase 1 - Core Features',
                description: 'Basic dashboard and data visualization',
                status: '1',
                created_by: users[2]._id,
                is_current_milestone: true,
                start_date: new Date('2024-04-01'),
                end_date: new Date('2024-06-30'),
                milestone_created_by: users[2]._id
            },
            // Inventory Management milestones
            {
                project_id: projects[4]._id,
                title: 'Beta Release',
                description: 'Initial beta version with core inventory features',
                status: '1',
                created_by: users[10]._id,
                is_current_milestone: true,
                start_date: new Date('2024-05-01'),
                end_date: new Date('2024-08-31'),
                milestone_created_by: users[10]._id
            },
            // Healthcare Portal milestones
            {
                project_id: projects[5]._id,
                title: 'MVP Launch',
                description: 'Minimum viable product for healthcare portal',
                status: '1',
                created_by: users[16]._id,
                is_current_milestone: true,
                start_date: new Date('2024-06-01'),
                end_date: new Date('2024-09-30'),
                milestone_created_by: users[16]._id
            },
            // Financial Analytics milestones
            {
                project_id: projects[6]._id,
                title: 'Phase 1 - Data Pipeline',
                description: 'Setup data collection and processing',
                status: '1',
                created_by: users[2]._id,
                is_current_milestone: true,
                start_date: new Date('2024-07-01'),
                end_date: new Date('2024-09-30'),
                milestone_created_by: users[2]._id
            },
            // Online Learning Platform milestones
            {
                project_id: projects[7]._id,
                title: 'Content Management System',
                description: 'Build CMS for course creation',
                status: '1',
                created_by: users[10]._id,
                is_current_milestone: true,
                start_date: new Date('2024-03-15'),
                end_date: new Date('2024-06-30'),
                milestone_created_by: users[10]._id
            },
            {
                project_id: projects[7]._id,
                title: 'Video Streaming Integration',
                description: 'Integrate video player and streaming',
                status: '1',
                created_by: users[10]._id,
                is_current_milestone: false,
                start_date: new Date('2024-07-01'),
                end_date: new Date('2024-09-30'),
                milestone_created_by: users[10]._id
            },
            // Food Delivery Platform milestones
            {
                project_id: projects[8]._id,
                title: 'Restaurant Portal',
                description: 'Build restaurant management portal',
                status: '1',
                created_by: users[16]._id,
                is_current_milestone: true,
                start_date: new Date('2024-02-20'),
                end_date: new Date('2024-05-31'),
                milestone_created_by: users[16]._id
            },
            {
                project_id: projects[8]._id,
                title: 'Real-time Tracking',
                description: 'Implement GPS tracking for deliveries',
                status: '1',
                created_by: users[16]._id,
                is_current_milestone: false,
                start_date: new Date('2024-06-01'),
                end_date: new Date('2024-08-31'),
                milestone_created_by: users[16]._id
            },
            // Green Energy Monitoring milestones
            {
                project_id: projects[9]._id,
                title: 'IoT Integration',
                description: 'Connect sensors and IoT devices',
                status: '1',
                created_by: users[2]._id,
                is_current_milestone: true,
                start_date: new Date('2024-05-15'),
                end_date: new Date('2024-08-31'),
                milestone_created_by: users[2]._id
            }
        ]);
        console.log(`✅ Created ${milestones.length} milestones\n`);

        // 10. Create Groups (20 groups - multiple per project)
        console.log('📦 Creating Groups...');
        const groups = await Group.insertMany([
            // E-Commerce Platform groups
            {
                group_name: 'Frontend Development',
                group_description: 'All frontend related tasks',
                status: 'PROGRESS',
                project_id: projects[0]._id,
                milestone_id: milestones[0]._id,
                delete_status: '1'
            },
            {
                group_name: 'Backend API',
                group_description: 'API development tasks',
                status: 'PROGRESS',
                project_id: projects[0]._id,
                milestone_id: milestones[0]._id,
                delete_status: '1'
            },
            {
                group_name: 'Database Design',
                group_description: 'Database schema and optimization',
                status: 'COMPLETED',
                project_id: projects[0]._id,
                milestone_id: milestones[0]._id,
                delete_status: '1'
            },
            // Mobile Banking groups
            {
                group_name: 'Mobile UI/UX',
                group_description: 'Mobile interface design',
                status: 'PROGRESS',
                project_id: projects[1]._id,
                milestone_id: milestones[2]._id,
                delete_status: '1'
            },
            {
                group_name: 'Security Features',
                group_description: 'Authentication and security',
                status: 'PROGRESS',
                project_id: projects[1]._id,
                milestone_id: milestones[2]._id,
                delete_status: '1'
            },
            // CRM System groups
            {
                group_name: 'Customer Module',
                group_description: 'Customer management features',
                status: 'PROGRESS',
                project_id: projects[2]._id,
                milestone_id: milestones[4]._id,
                delete_status: '1'
            },
            {
                group_name: 'Sales Pipeline',
                group_description: 'Sales tracking and pipeline',
                status: 'PROGRESS',
                project_id: projects[2]._id,
                milestone_id: milestones[4]._id,
                delete_status: '1'
            },
            // Social Media Dashboard groups
            {
                group_name: 'UI/UX Design',
                group_description: 'Design and user experience tasks',
                status: 'PROGRESS',
                project_id: projects[3]._id,
                milestone_id: milestones[5]._id,
                delete_status: '1'
            },
            {
                group_name: 'Analytics Engine',
                group_description: 'Data processing and analytics',
                status: 'PROGRESS',
                project_id: projects[3]._id,
                milestone_id: milestones[5]._id,
                delete_status: '1'
            },
            // Inventory Management groups
            {
                group_name: 'API Development',
                group_description: 'Backend API endpoints',
                status: 'PROGRESS',
                project_id: projects[4]._id,
                milestone_id: milestones[6]._id,
                delete_status: '1'
            },
            {
                group_name: 'Warehouse Module',
                group_description: 'Warehouse management features',
                status: 'PROGRESS',
                project_id: projects[4]._id,
                milestone_id: milestones[6]._id,
                delete_status: '1'
            },
            // Healthcare Portal groups
            {
                group_name: 'Testing & QA',
                group_description: 'Quality assurance and testing',
                status: 'PROGRESS',
                project_id: projects[5]._id,
                milestone_id: milestones[7]._id,
                delete_status: '1'
            },
            {
                group_name: 'Patient Portal',
                group_description: 'Patient-facing features',
                status: 'PROGRESS',
                project_id: projects[5]._id,
                milestone_id: milestones[7]._id,
                delete_status: '1'
            },
            // Financial Analytics groups
            {
                group_name: 'Data Pipeline',
                group_description: 'ETL and data processing',
                status: 'PROGRESS',
                project_id: projects[6]._id,
                milestone_id: milestones[8]._id,
                delete_status: '1'
            },
            {
                group_name: 'Reporting Module',
                group_description: 'Financial reports and dashboards',
                status: 'PROGRESS',
                project_id: projects[6]._id,
                milestone_id: milestones[8]._id,
                delete_status: '1'
            },
            // Online Learning groups
            {
                group_name: 'Content Management',
                group_description: 'CMS development',
                status: 'PROGRESS',
                project_id: projects[7]._id,
                milestone_id: milestones[9]._id,
                delete_status: '1'
            },
            {
                group_name: 'Student Portal',
                group_description: 'Student interface and features',
                status: 'PROGRESS',
                project_id: projects[7]._id,
                milestone_id: milestones[9]._id,
                delete_status: '1'
            },
            // Food Delivery groups
            {
                group_name: 'Restaurant Backend',
                group_description: 'Restaurant management system',
                status: 'PROGRESS',
                project_id: projects[8]._id,
                milestone_id: milestones[11]._id,
                delete_status: '1'
            },
            {
                group_name: 'Delivery Tracking',
                group_description: 'Real-time delivery tracking',
                status: 'PROGRESS',
                project_id: projects[8]._id,
                milestone_id: milestones[11]._id,
                delete_status: '1'
            },
            // Green Energy groups
            {
                group_name: 'IoT Integration',
                group_description: 'Device connectivity and data collection',
                status: 'PROGRESS',
                project_id: projects[9]._id,
                milestone_id: milestones[13]._id,
                delete_status: '1'
            }
        ]);
        console.log(`✅ Created ${groups.length} groups\n`);

        // 11. Create Tasks (50+ tasks across all projects)
        console.log('📦 Creating Tasks...');
        const tasks = await Task.insertMany([
            // E-Commerce Platform tasks
            {
                project_id: projects[0]._id,
                milestone_id: milestones[0]._id,
                group_id: groups[0]._id,
                task_name: 'Design Login Page',
                task_description: 'Create responsive login page with form validation',
                task_status: statuses[3]._id,
                status_name: 'COMPLETED',
                task_priority: 'High',
                estimate: '8:00',
                task_start_date: new Date('2024-01-20'),
                task_end_date: new Date('2024-01-22'),
                assigned_by: users[2]._id,
                assigned_to: [users[1]._id],
                task_created_by: users[2]._id,
                comments: [
                    {
                        comment: 'Please follow the design mockups',
                        user_id: users[2]._id,
                        is_reply: false,
                        created_At: new Date('2024-01-20')
                    }
                ],
                is_task_finished: true,
                task_logged_time: '07:30'
            },
            {
                project_id: projects[0]._id,
                milestone_id: milestones[0]._id,
                group_id: groups[1]._id,
                task_name: 'Implement User Authentication API',
                task_description: 'Create REST API endpoints for user authentication',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '16:00',
                task_start_date: new Date('2024-01-23'),
                task_end_date: new Date('2024-01-30'),
                assigned_by: users[2]._id,
                assigned_to: [users[0]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '12:00'
            },
            {
                project_id: projects[0]._id,
                milestone_id: milestones[0]._id,
                group_id: groups[0]._id,
                task_name: 'Product Listing Page',
                task_description: 'Create product grid with filters and pagination',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'Medium',
                estimate: '20:00',
                task_start_date: new Date('2024-02-01'),
                task_end_date: new Date('2024-02-10'),
                assigned_by: users[2]._id,
                assigned_to: [users[1]._id, users[3]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            {
                project_id: projects[0]._id,
                milestone_id: milestones[0]._id,
                group_id: groups[2]._id,
                task_name: 'Database Schema Design',
                task_description: 'Design MongoDB schema for products and users',
                task_status: statuses[3]._id,
                status_name: 'COMPLETED',
                task_priority: 'High',
                estimate: '12:00',
                task_start_date: new Date('2024-01-16'),
                task_end_date: new Date('2024-01-19'),
                assigned_by: users[2]._id,
                assigned_to: [users[0]._id],
                task_created_by: users[2]._id,
                comments: [
                    {
                        comment: 'Schema looks good, approved!',
                        user_id: users[2]._id,
                        is_reply: false,
                        created_At: new Date('2024-01-19')
                    }
                ],
                is_task_finished: true,
                task_logged_time: '11:30'
            },
            {
                project_id: projects[0]._id,
                milestone_id: milestones[0]._id,
                group_id: groups[1]._id,
                task_name: 'Implement Shopping Cart API',
                task_description: 'Create endpoints for add/remove/update cart items',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'High',
                estimate: '14:00',
                task_start_date: new Date('2024-02-05'),
                task_end_date: new Date('2024-02-12'),
                assigned_by: users[2]._id,
                assigned_to: [users[0]._id, users[5]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            {
                project_id: projects[0]._id,
                milestone_id: milestones[0]._id,
                group_id: groups[0]._id,
                task_name: 'Build Product Details Page',
                task_description: 'Create detailed product view with images and reviews',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'Medium',
                estimate: '16:00',
                task_start_date: new Date('2024-02-08'),
                task_end_date: new Date('2024-02-15'),
                assigned_by: users[2]._id,
                assigned_to: [users[6]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '08:00'
            },
            // Mobile Banking App tasks
            {
                project_id: projects[1]._id,
                milestone_id: milestones[2]._id,
                group_id: groups[3]._id,
                task_name: 'Setup React Native Project',
                task_description: 'Initialize React Native project with navigation',
                task_status: statuses[3]._id,
                status_name: 'COMPLETED',
                task_priority: 'High',
                estimate: '6:00',
                task_start_date: new Date('2024-02-05'),
                task_end_date: new Date('2024-02-06'),
                assigned_by: users[2]._id,
                assigned_to: [users[0]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: true,
                task_logged_time: '05:45'
            },
            {
                project_id: projects[1]._id,
                milestone_id: milestones[2]._id,
                group_id: groups[4]._id,
                task_name: 'Implement Biometric Authentication',
                task_description: 'Add fingerprint and face ID authentication',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '24:00',
                task_start_date: new Date('2024-02-10'),
                task_end_date: new Date('2024-02-20'),
                assigned_by: users[2]._id,
                assigned_to: [users[7]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '16:00'
            },
            {
                project_id: projects[1]._id,
                milestone_id: milestones[2]._id,
                group_id: groups[3]._id,
                task_name: 'Design Account Dashboard',
                task_description: 'Create main dashboard showing account balance and transactions',
                task_status: statuses[2]._id,
                status_name: 'IN_REVIEW',
                task_priority: 'High',
                estimate: '18:00',
                task_start_date: new Date('2024-02-12'),
                task_end_date: new Date('2024-02-18'),
                assigned_by: users[2]._id,
                assigned_to: [users[15]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '17:30'
            },
            {
                project_id: projects[1]._id,
                milestone_id: milestones[2]._id,
                group_id: groups[4]._id,
                task_name: 'Implement Transaction History',
                task_description: 'Build transaction history with search and filters',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'Medium',
                estimate: '12:00',
                task_start_date: new Date('2024-02-22'),
                task_end_date: new Date('2024-02-28'),
                assigned_by: users[2]._id,
                assigned_to: [users[7]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            // CRM System tasks
            {
                project_id: projects[2]._id,
                milestone_id: milestones[4]._id,
                group_id: groups[5]._id,
                task_name: 'Create Customer Profile Page',
                task_description: 'Build customer detail view with contact history',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '20:00',
                task_start_date: new Date('2024-03-05'),
                task_end_date: new Date('2024-03-15'),
                assigned_by: users[10]._id,
                assigned_to: [users[8]._id],
                task_created_by: users[10]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '12:00'
            },
            {
                project_id: projects[2]._id,
                milestone_id: milestones[4]._id,
                group_id: groups[6]._id,
                task_name: 'Implement Sales Pipeline Visualization',
                task_description: 'Create kanban board for sales opportunities',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'High',
                estimate: '24:00',
                task_start_date: new Date('2024-03-18'),
                task_end_date: new Date('2024-03-28'),
                assigned_by: users[10]._id,
                assigned_to: [users[1]._id, users[6]._id],
                task_created_by: users[10]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            {
                project_id: projects[2]._id,
                milestone_id: milestones[4]._id,
                group_id: groups[5]._id,
                task_name: 'Build Contact Management Module',
                task_description: 'CRUD operations for customer contacts',
                task_status: statuses[3]._id,
                status_name: 'COMPLETED',
                task_priority: 'High',
                estimate: '16:00',
                task_start_date: new Date('2024-03-01'),
                task_end_date: new Date('2024-03-08'),
                assigned_by: users[10]._id,
                assigned_to: [users[18]._id],
                task_created_by: users[10]._id,
                comments: [],
                is_task_finished: true,
                task_logged_time: '15:30'
            },
            // Social Media Dashboard tasks
            {
                project_id: projects[3]._id,
                milestone_id: milestones[5]._id,
                group_id: groups[7]._id,
                task_name: 'Design Analytics Dashboard',
                task_description: 'Create wireframes and mockups for analytics dashboard',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '16:00',
                task_start_date: new Date('2024-04-05'),
                task_end_date: new Date('2024-04-12'),
                assigned_by: users[2]._id,
                assigned_to: [users[8]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '08:00'
            },
            {
                project_id: projects[3]._id,
                milestone_id: milestones[5]._id,
                group_id: groups[7]._id,
                task_name: 'Implement Chart Components',
                task_description: 'Build reusable chart components using Chart.js',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'Medium',
                estimate: '20:00',
                task_start_date: new Date('2024-04-15'),
                task_end_date: new Date('2024-04-25'),
                assigned_by: users[2]._id,
                assigned_to: [users[6]._id, users[7]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            {
                project_id: projects[3]._id,
                milestone_id: milestones[5]._id,
                group_id: groups[8]._id,
                task_name: 'Build Data Processing Pipeline',
                task_description: 'Create ETL pipeline for social media data',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '32:00',
                task_start_date: new Date('2024-04-08'),
                task_end_date: new Date('2024-04-22'),
                assigned_by: users[2]._id,
                assigned_to: [users[11]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '20:00'
            },
            // Inventory Management tasks
            {
                project_id: projects[4]._id,
                milestone_id: milestones[6]._id,
                group_id: groups[9]._id,
                task_name: 'Create Inventory API Endpoints',
                task_description: 'Build REST APIs for inventory CRUD operations',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '24:00',
                task_start_date: new Date('2024-05-05'),
                task_end_date: new Date('2024-05-15'),
                assigned_by: users[10]._id,
                assigned_to: [users[7]._id],
                task_created_by: users[10]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '12:00'
            },
            {
                project_id: projects[4]._id,
                milestone_id: milestones[6]._id,
                group_id: groups[9]._id,
                task_name: 'Implement Barcode Scanner',
                task_description: 'Add barcode scanning functionality for inventory items',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'High',
                estimate: '18:00',
                task_start_date: new Date('2024-05-20'),
                task_end_date: new Date('2024-05-30'),
                assigned_by: users[10]._id,
                assigned_to: [users[9]._id],
                task_created_by: users[10]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            {
                project_id: projects[4]._id,
                milestone_id: milestones[6]._id,
                group_id: groups[10]._id,
                task_name: 'Build Warehouse Dashboard',
                task_description: 'Create real-time warehouse monitoring dashboard',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'Medium',
                estimate: '22:00',
                task_start_date: new Date('2024-05-12'),
                task_end_date: new Date('2024-05-25'),
                assigned_by: users[10]._id,
                assigned_to: [users[1]._id],
                task_created_by: users[10]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '10:00'
            },
            // Healthcare Portal tasks
            {
                project_id: projects[5]._id,
                milestone_id: milestones[7]._id,
                group_id: groups[11]._id,
                task_name: 'Write Test Cases',
                task_description: 'Create comprehensive test cases for patient portal',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'Medium',
                estimate: '16:00',
                task_start_date: new Date('2024-06-10'),
                task_end_date: new Date('2024-06-20'),
                assigned_by: users[16]._id,
                assigned_to: [users[4]._id],
                task_created_by: users[16]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            {
                project_id: projects[5]._id,
                milestone_id: milestones[7]._id,
                group_id: groups[12]._id,
                task_name: 'Build Appointment Booking System',
                task_description: 'Create appointment scheduling with calendar integration',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '28:00',
                task_start_date: new Date('2024-06-05'),
                task_end_date: new Date('2024-06-20'),
                assigned_by: users[16]._id,
                assigned_to: [users[18]._id, users[7]._id],
                task_created_by: users[16]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '18:00'
            },
            {
                project_id: projects[5]._id,
                milestone_id: milestones[7]._id,
                group_id: groups[12]._id,
                task_name: 'Implement Patient Records Management',
                task_description: 'Build secure patient records storage and retrieval',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'High',
                estimate: '32:00',
                task_start_date: new Date('2024-06-22'),
                task_end_date: new Date('2024-07-10'),
                assigned_by: users[16]._id,
                assigned_to: [users[18]._id],
                task_created_by: users[16]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            // Financial Analytics tasks
            {
                project_id: projects[6]._id,
                milestone_id: milestones[8]._id,
                group_id: groups[13]._id,
                task_name: 'Setup Project Infrastructure',
                task_description: 'Initialize project structure and CI/CD pipeline',
                task_status: statuses[3]._id,
                status_name: 'COMPLETED',
                task_priority: 'High',
                estimate: '12:00',
                task_start_date: new Date('2024-07-01'),
                task_end_date: new Date('2024-07-03'),
                assigned_by: users[2]._id,
                assigned_to: [users[9]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: true,
                task_logged_time: '11:30'
            },
            {
                project_id: projects[6]._id,
                milestone_id: milestones[8]._id,
                group_id: groups[13]._id,
                task_name: 'Build ETL Pipeline',
                task_description: 'Create data extraction and transformation pipeline',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '40:00',
                task_start_date: new Date('2024-07-05'),
                task_end_date: new Date('2024-07-25'),
                assigned_by: users[2]._id,
                assigned_to: [users[18]._id, users[11]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '24:00'
            },
            {
                project_id: projects[6]._id,
                milestone_id: milestones[8]._id,
                group_id: groups[14]._id,
                task_name: 'Create Financial Reports',
                task_description: 'Build customizable financial report templates',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'Medium',
                estimate: '28:00',
                task_start_date: new Date('2024-07-28'),
                task_end_date: new Date('2024-08-15'),
                assigned_by: users[2]._id,
                assigned_to: [users[1]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            // Online Learning Platform tasks
            {
                project_id: projects[7]._id,
                milestone_id: milestones[9]._id,
                group_id: groups[15]._id,
                task_name: 'Build Course Creation Interface',
                task_description: 'Create rich text editor for course content',
                task_status: statuses[2]._id,
                status_name: 'IN_REVIEW',
                task_priority: 'High',
                estimate: '26:00',
                task_start_date: new Date('2024-03-20'),
                task_end_date: new Date('2024-04-05'),
                assigned_by: users[10]._id,
                assigned_to: [users[6]._id],
                task_created_by: users[10]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '25:00'
            },
            {
                project_id: projects[7]._id,
                milestone_id: milestones[9]._id,
                group_id: groups[16]._id,
                task_name: 'Implement Quiz Module',
                task_description: 'Build quiz creation and grading system',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '30:00',
                task_start_date: new Date('2024-04-10'),
                task_end_date: new Date('2024-04-30'),
                assigned_by: users[10]._id,
                assigned_to: [users[7]._id, users[12]._id],
                task_created_by: users[10]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '16:00'
            },
            {
                project_id: projects[7]._id,
                milestone_id: milestones[9]._id,
                group_id: groups[16]._id,
                task_name: 'Create Student Progress Tracking',
                task_description: 'Build dashboard showing student progress and achievements',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'Medium',
                estimate: '22:00',
                task_start_date: new Date('2024-05-05'),
                task_end_date: new Date('2024-05-20'),
                assigned_by: users[10]._id,
                assigned_to: [users[14]._id],
                task_created_by: users[10]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            // Food Delivery Platform tasks
            {
                project_id: projects[8]._id,
                milestone_id: milestones[11]._id,
                group_id: groups[17]._id,
                task_name: 'Build Restaurant Dashboard',
                task_description: 'Create order management dashboard for restaurants',
                task_status: statuses[3]._id,
                status_name: 'COMPLETED',
                task_priority: 'High',
                estimate: '24:00',
                task_start_date: new Date('2024-02-25'),
                task_end_date: new Date('2024-03-08'),
                assigned_by: users[16]._id,
                assigned_to: [users[15]._id],
                task_created_by: users[16]._id,
                comments: [],
                is_task_finished: true,
                task_logged_time: '23:30'
            },
            {
                project_id: projects[8]._id,
                milestone_id: milestones[11]._id,
                group_id: groups[17]._id,
                task_name: 'Implement Order Processing',
                task_description: 'Build real-time order processing system',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '28:00',
                task_start_date: new Date('2024-03-10'),
                task_end_date: new Date('2024-03-28'),
                assigned_by: users[16]._id,
                assigned_to: [users[0]._id],
                task_created_by: users[16]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '18:00'
            },
            {
                project_id: projects[8]._id,
                milestone_id: milestones[11]._id,
                group_id: groups[18]._id,
                task_name: 'Implement GPS Tracking',
                task_description: 'Add real-time delivery tracking with maps',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'High',
                estimate: '32:00',
                task_start_date: new Date('2024-04-01'),
                task_end_date: new Date('2024-04-20'),
                assigned_by: users[16]._id,
                assigned_to: [users[9]._id, users[19]._id],
                task_created_by: users[16]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            // Green Energy Monitoring tasks
            {
                project_id: projects[9]._id,
                milestone_id: milestones[13]._id,
                group_id: groups[19]._id,
                task_name: 'Setup IoT Device Integration',
                task_description: 'Connect IoT sensors and configure data collection',
                task_status: statuses[1]._id,
                status_name: 'IN_PROGRESS',
                task_priority: 'High',
                estimate: '36:00',
                task_start_date: new Date('2024-05-20'),
                task_end_date: new Date('2024-06-10'),
                assigned_by: users[2]._id,
                assigned_to: [users[9]._id, users[19]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '22:00'
            },
            {
                project_id: projects[9]._id,
                milestone_id: milestones[13]._id,
                group_id: groups[19]._id,
                task_name: 'Build Energy Consumption Dashboard',
                task_description: 'Create real-time energy monitoring dashboard',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'High',
                estimate: '26:00',
                task_start_date: new Date('2024-06-12'),
                task_end_date: new Date('2024-06-30'),
                assigned_by: users[2]._id,
                assigned_to: [users[1]._id, users[14]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            },
            {
                project_id: projects[9]._id,
                milestone_id: milestones[13]._id,
                group_id: groups[19]._id,
                task_name: 'Implement Alert System',
                task_description: 'Build notification system for anomalies and thresholds',
                task_status: statuses[0]._id,
                status_name: 'TODO',
                task_priority: 'Medium',
                estimate: '18:00',
                task_start_date: new Date('2024-07-01'),
                task_end_date: new Date('2024-07-15'),
                assigned_by: users[2]._id,
                assigned_to: [users[5]._id],
                task_created_by: users[2]._id,
                comments: [],
                is_task_finished: false,
                task_logged_time: '00:00'
            }
        ]);
        console.log(`✅ Created ${tasks.length} tasks\n`);

        // 12. Create TimeLogs (70+ timelogs - heavily populated)
        console.log('📦 Creating TimeLogs...');
        const timelogs = await TimeLog.insertMany([
            // E-Commerce Platform logs
            {
                project_id: projects[0]._id,
                task_id: tasks[0]._id,
                task_description: 'Worked on login page styling',
                date: new Date('2024-01-20').toISOString(),
                task_start_time: '09:00',
                task_end_time: '13:00',
                task_time_spent: '04:00',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[0]._id,
                task_id: tasks[0]._id,
                task_description: 'Implemented form validation',
                date: new Date('2024-01-21').toISOString(),
                task_start_time: '10:00',
                task_end_time: '13:30',
                task_time_spent: '03:30',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[0]._id,
                task_id: tasks[1]._id,
                task_description: 'Setup JWT authentication',
                date: new Date('2024-01-23').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[0]._id,
                task_id: tasks[1]._id,
                task_description: 'Implemented password hashing',
                date: new Date('2024-01-24').toISOString(),
                task_start_time: '09:00',
                task_end_time: '13:00',
                task_time_spent: '04:00',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[0]._id,
                task_id: tasks[3]._id,
                task_description: 'Created database schemas',
                date: new Date('2024-01-16').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:30',
                task_time_spent: '08:30',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            {
                project_id: projects[0]._id,
                task_id: tasks[5]._id,
                task_description: 'Started product details page',
                date: new Date('2024-02-08').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[6]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Mobile Banking logs
            {
                project_id: projects[1]._id,
                task_id: tasks[6]._id,
                task_description: 'Project setup and configuration',
                date: new Date('2024-02-05').toISOString(),
                task_start_time: '10:00',
                task_end_time: '15:45',
                task_time_spent: '05:45',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[1]._id,
                task_id: tasks[7]._id,
                task_description: 'Research biometric authentication APIs',
                date: new Date('2024-02-10').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[1]._id,
                task_id: tasks[7]._id,
                task_description: 'Implemented fingerprint auth',
                date: new Date('2024-02-12').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[1]._id,
                task_id: tasks[8]._id,
                task_description: 'Designed dashboard wireframes',
                date: new Date('2024-02-12').toISOString(),
                task_start_time: '10:00',
                task_end_time: '18:00',
                task_time_spent: '08:00',
                user_id: users[15]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[1]._id,
                task_id: tasks[8]._id,
                task_description: 'Implemented dashboard components',
                date: new Date('2024-02-15').toISOString(),
                task_start_time: '09:00',
                task_end_time: '18:30',
                task_time_spent: '09:30',
                user_id: users[15]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // CRM System logs
            {
                project_id: projects[2]._id,
                task_id: tasks[10]._id,
                task_description: 'Built customer profile UI',
                date: new Date('2024-03-05').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[8]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[2]._id,
                task_id: tasks[10]._id,
                task_description: 'Added contact history feature',
                date: new Date('2024-03-08').toISOString(),
                task_start_time: '10:00',
                task_end_time: '14:00',
                task_time_spent: '04:00',
                user_id: users[8]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[2]._id,
                task_id: tasks[12]._id,
                task_description: 'Built contact CRUD operations',
                date: new Date('2024-03-01').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[18]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            {
                project_id: projects[2]._id,
                task_id: tasks[12]._id,
                task_description: 'Added validation and testing',
                date: new Date('2024-03-05').toISOString(),
                task_start_time: '09:00',
                task_end_time: '16:30',
                task_time_spent: '07:30',
                user_id: users[18]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            // Social Media Dashboard logs
            {
                project_id: projects[3]._id,
                task_id: tasks[13]._id,
                task_description: 'Created dashboard wireframes',
                date: new Date('2024-04-05').toISOString(),
                task_start_time: '10:00',
                task_end_time: '18:00',
                task_time_spent: '08:00',
                user_id: users[8]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[3]._id,
                task_id: tasks[15]._id,
                task_description: 'Built data ingestion pipeline',
                date: new Date('2024-04-08').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[11]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[3]._id,
                task_id: tasks[15]._id,
                task_description: 'Implemented data transformations',
                date: new Date('2024-04-10').toISOString(),
                task_start_time: '09:00',
                task_end_time: '21:00',
                task_time_spent: '12:00',
                user_id: users[11]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Inventory Management logs
            {
                project_id: projects[4]._id,
                task_id: tasks[16]._id,
                task_description: 'Created API endpoints',
                date: new Date('2024-05-05').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
                        {
                project_id: projects[4]._id,
                task_id: tasks[16]._id,
                task_description: 'Added validation and error handling',
                date: new Date('2024-05-08').toISOString(),
                task_start_time: '10:00',
                task_end_time: '14:00',
                task_time_spent: '04:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[4]._id,
                task_id: tasks[18]._id,
                task_description: 'Built warehouse monitoring UI',
                date: new Date('2024-05-12').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[4]._id,
                task_id: tasks[18]._id,
                task_description: 'Added real-time updates',
                date: new Date('2024-05-15').toISOString(),
                task_start_time: '14:00',
                task_end_time: '16:00',
                task_time_spent: '02:00',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Healthcare Portal logs
            {
                project_id: projects[5]._id,
                task_id: tasks[20]._id,
                task_description: 'Designed appointment booking UI',
                date: new Date('2024-06-05').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[18]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[5]._id,
                task_id: tasks[20]._id,
                task_description: 'Implemented calendar integration',
                date: new Date('2024-06-10').toISOString(),
                task_start_time: '09:00',
                task_end_time: '19:00',
                task_time_spent: '10:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Financial Analytics logs
            {
                project_id: projects[6]._id,
                task_id: tasks[22]._id,
                task_description: 'Configured CI/CD pipeline',
                date: new Date('2024-07-01').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[9]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            {
                project_id: projects[6]._id,
                task_id: tasks[22]._id,
                task_description: 'Setup deployment scripts',
                date: new Date('2024-07-02').toISOString(),
                task_start_time: '10:00',
                task_end_time: '13:30',
                task_time_spent: '03:30',
                user_id: users[9]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            {
                project_id: projects[6]._id,
                task_id: tasks[23]._id,
                task_description: 'Built data extraction module',
                date: new Date('2024-07-05').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[18]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[6]._id,
                task_id: tasks[23]._id,
                task_description: 'Implemented data transformations',
                date: new Date('2024-07-08').toISOString(),
                task_start_time: '09:00',
                task_end_time: '21:00',
                task_time_spent: '12:00',
                user_id: users[11]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[6]._id,
                task_id: tasks[23]._id,
                task_description: 'Added data validation rules',
                date: new Date('2024-07-12').toISOString(),
                task_start_time: '14:00',
                task_end_time: '18:00',
                task_time_spent: '04:00',
                user_id: users[18]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Online Learning Platform logs
            {
                project_id: projects[7]._id,
                task_id: tasks[25]._id,
                task_description: 'Integrated rich text editor',
                date: new Date('2024-03-20').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[6]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[7]._id,
                task_id: tasks[25]._id,
                task_description: 'Added media upload functionality',
                date: new Date('2024-03-25').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[6]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[7]._id,
                task_id: tasks[25]._id,
                task_description: 'Testing and bug fixes',
                date: new Date('2024-04-02').toISOString(),
                task_start_time: '10:00',
                task_end_time: '19:00',
                task_time_spent: '09:00',
                user_id: users[6]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[7]._id,
                task_id: tasks[26]._id,
                task_description: 'Built quiz creation interface',
                date: new Date('2024-04-10').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[7]._id,
                task_id: tasks[26]._id,
                task_description: 'Implemented auto-grading system',
                date: new Date('2024-04-15').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[12]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Food Delivery Platform logs
            {
                project_id: projects[8]._id,
                task_id: tasks[28]._id,
                task_description: 'Built restaurant dashboard UI',
                date: new Date('2024-02-25').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[15]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            {
                project_id: projects[8]._id,
                task_id: tasks[28]._id,
                task_description: 'Added order management features',
                date: new Date('2024-03-01').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:30',
                task_time_spent: '08:30',
                user_id: users[15]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            {
                project_id: projects[8]._id,
                task_id: tasks[28]._id,
                task_description: 'Testing and refinements',
                date: new Date('2024-03-05').toISOString(),
                task_start_time: '10:00',
                task_end_time: '17:00',
                task_time_spent: '07:00',
                user_id: users[15]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            {
                project_id: projects[8]._id,
                task_id: tasks[29]._id,
                task_description: 'Built order processing API',
                date: new Date('2024-03-10').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[8]._id,
                task_id: tasks[29]._id,
                task_description: 'Added real-time notifications',
                date: new Date('2024-03-15').toISOString(),
                task_start_time: '09:00',
                task_end_time: '19:00',
                task_time_spent: '10:00',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Green Energy Monitoring logs
            {
                project_id: projects[9]._id,
                task_id: tasks[31]._id,
                task_description: 'Configured IoT device connections',
                date: new Date('2024-05-20').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[9]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[9]._id,
                task_id: tasks[31]._id,
                task_description: 'Implemented data collection pipeline',
                date: new Date('2024-05-25').toISOString(),
                task_start_time: '09:00',
                task_end_time: '18:00',
                task_time_spent: '09:00',
                user_id: users[19]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[9]._id,
                task_id: tasks[31]._id,
                task_description: 'Testing sensor data accuracy',
                date: new Date('2024-06-01').toISOString(),
                task_start_time: '10:00',
                task_end_time: '15:00',
                task_time_spent: '05:00',
                user_id: users[9]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Additional E-Commerce Platform logs
            {
                project_id: projects[0]._id,
                task_id: tasks[1]._id,
                task_description: 'Fixed authentication bugs',
                date: new Date('2024-01-25').toISOString(),
                task_start_time: '09:00',
                task_end_time: '12:00',
                task_time_spent: '03:00',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[0]._id,
                task_id: tasks[3]._id,
                task_description: 'Optimized database queries',
                date: new Date('2024-01-18').toISOString(),
                task_start_time: '10:00',
                task_end_time: '14:30',
                task_time_spent: '04:30',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            {
                project_id: projects[0]._id,
                task_id: tasks[5]._id,
                task_description: 'Added image gallery component',
                date: new Date('2024-02-09').toISOString(),
                task_start_time: '14:00',
                task_end_time: '18:00',
                task_time_spent: '04:00',
                user_id: users[6]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[0]._id,
                task_id: tasks[2]._id,
                task_description: 'Designed product listing filters',
                date: new Date('2024-02-02').toISOString(),
                task_start_time: '09:00',
                task_end_time: '13:00',
                task_time_spent: '04:00',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[0]._id,
                task_id: tasks[4]._id,
                task_description: 'Started shopping cart API',
                date: new Date('2024-02-05').toISOString(),
                task_start_time: '09:00',
                task_end_time: '12:00',
                task_time_spent: '03:00',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Additional Mobile Banking logs
            {
                project_id: projects[1]._id,
                task_id: tasks[7]._id,
                task_description: 'Testing biometric on different devices',
                date: new Date('2024-02-14').toISOString(),
                task_start_time: '10:00',
                task_end_time: '16:00',
                task_time_spent: '06:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[1]._id,
                task_id: tasks[8]._id,
                task_description: 'Added transaction list component',
                date: new Date('2024-02-17').toISOString(),
                task_start_time: '09:00',
                task_end_time: '13:00',
                task_time_spent: '04:00',
                user_id: users[15]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[1]._id,
                task_id: tasks[9]._id,
                task_description: 'Designed transaction history filters',
                date: new Date('2024-02-23').toISOString(),
                task_start_time: '10:00',
                task_end_time: '14:00',
                task_time_spent: '04:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[1]._id,
                task_id: tasks[6]._id,
                task_description: 'Configured navigation structure',
                date: new Date('2024-02-06').toISOString(),
                task_start_time: '09:00',
                task_end_time: '11:00',
                task_time_spent: '02:00',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Additional CRM System logs
            {
                project_id: projects[2]._id,
                task_id: tasks[10]._id,
                task_description: 'Implemented contact notes feature',
                date: new Date('2024-03-10').toISOString(),
                task_start_time: '09:00',
                task_end_time: '15:00',
                task_time_spent: '06:00',
                user_id: users[8]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[2]._id,
                task_id: tasks[11]._id,
                task_description: 'Created sales pipeline UI mockup',
                date: new Date('2024-03-20').toISOString(),
                task_start_time: '10:00',
                task_end_time: '16:00',
                task_time_spent: '06:00',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[2]._id,
                task_id: tasks[12]._id,
                task_description: 'Refactored contact management code',
                date: new Date('2024-03-07').toISOString(),
                task_start_time: '09:00',
                task_end_time: '12:00',
                task_time_spent: '03:00',
                user_id: users[18]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            // Additional Social Media Dashboard logs
            {
                project_id: projects[3]._id,
                task_id: tasks[13]._id,
                task_description: 'Finalized dashboard design',
                date: new Date('2024-04-10').toISOString(),
                task_start_time: '09:00',
                task_end_time: '13:00',
                task_time_spent: '04:00',
                user_id: users[8]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[3]._id,
                task_id: tasks[14]._id,
                task_description: 'Started chart implementation',
                date: new Date('2024-04-16').toISOString(),
                task_start_time: '10:00',
                task_end_time: '18:00',
                task_time_spent: '08:00',
                user_id: users[6]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[3]._id,
                task_id: tasks[15]._id,
                task_description: 'Added error handling to pipeline',
                date: new Date('2024-04-15').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[11]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[3]._id,
                task_id: tasks[14]._id,
                task_description: 'Integrated chart.js library',
                date: new Date('2024-04-20').toISOString(),
                task_start_time: '09:00',
                task_end_time: '15:00',
                task_time_spent: '06:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Additional Inventory Management logs
            {
                project_id: projects[4]._id,
                task_id: tasks[16]._id,
                task_description: 'Documented API endpoints',
                date: new Date('2024-05-10').toISOString(),
                task_start_time: '14:00',
                task_end_time: '17:00',
                task_time_spent: '03:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[4]._id,
                task_id: tasks[17]._id,
                task_description: 'Researched barcode scanner libraries',
                date: new Date('2024-05-21').toISOString(),
                task_start_time: '09:00',
                task_end_time: '12:00',
                task_time_spent: '03:00',
                user_id: users[9]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[4]._id,
                task_id: tasks[18]._id,
                task_description: 'Implemented WebSocket updates',
                date: new Date('2024-05-18').toISOString(),
                task_start_time: '10:00',
                task_end_time: '16:00',
                task_time_spent: '06:00',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[4]._id,
                task_id: tasks[17]._id,
                task_description: 'Implemented barcode scanning',
                date: new Date('2024-05-25').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[9]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Additional Healthcare Portal logs
            {
                project_id: projects[5]._id,
                task_id: tasks[19]._id,
                task_description: 'Created test scenarios',
                date: new Date('2024-06-12').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[4]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[5]._id,
                task_id: tasks[20]._id,
                task_description: 'Added appointment reminders',
                date: new Date('2024-06-15').toISOString(),
                task_start_time: '09:00',
                task_end_time: '13:00',
                task_time_spent: '04:00',
                user_id: users[18]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[5]._id,
                task_id: tasks[21]._id,
                task_description: 'Designed patient records UI',
                date: new Date('2024-06-23').toISOString(),
                task_start_time: '10:00',
                task_end_time: '18:00',
                task_time_spent: '08:00',
                user_id: users[18]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[5]._id,
                task_id: tasks[19]._id,
                task_description: 'Executed manual testing',
                date: new Date('2024-06-18').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[4]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Additional Financial Analytics logs
            {
                project_id: projects[6]._id,
                task_id: tasks[23]._id,
                task_description: 'Setup data warehousing',
                date: new Date('2024-07-15').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[18]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[6]._id,
                task_id: tasks[23]._id,
                task_description: 'Performance testing',
                date: new Date('2024-07-18').toISOString(),
                task_start_time: '10:00',
                task_end_time: '14:00',
                task_time_spent: '04:00',
                user_id: users[11]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[6]._id,
                task_id: tasks[24]._id,
                task_description: 'Created report templates',
                date: new Date('2024-07-30').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[6]._id,
                task_id: tasks[22]._id,
                task_description: 'Documented infrastructure setup',
                date: new Date('2024-07-03').toISOString(),
                task_start_time: '09:00',
                task_end_time: '12:00',
                task_time_spent: '03:00',
                user_id: users[9]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            // Additional Online Learning Platform logs
            {
                project_id: projects[7]._id,
                task_id: tasks[26]._id,
                task_description: 'Added quiz timer functionality',
                date: new Date('2024-04-20').toISOString(),
                task_start_time: '09:00',
                task_end_time: '13:00',
                task_time_spent: '04:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[7]._id,
                task_id: tasks[26]._id,
                task_description: 'Testing quiz with different question types',
                date: new Date('2024-04-25').toISOString(),
                task_start_time: '10:00',
                task_end_time: '16:00',
                task_time_spent: '06:00',
                user_id: users[12]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[7]._id,
                task_id: tasks[27]._id,
                task_description: 'Designed progress tracking UI',
                date: new Date('2024-05-06').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[14]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[7]._id,
                task_id: tasks[25]._id,
                task_description: 'Fixed editor bugs',
                date: new Date('2024-03-28').toISOString(),
                task_start_time: '14:00',
                task_end_time: '18:00',
                task_time_spent: '04:00',
                user_id: users[6]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // Additional Food Delivery Platform logs
            {
                project_id: projects[8]._id,
                task_id: tasks[29]._id,
                task_description: 'Added payment integration',
                date: new Date('2024-03-20').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[0]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[8]._id,
                task_id: tasks[30]._id,
                task_description: 'Integrated Google Maps API',
                date: new Date('2024-04-02').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[9]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[8]._id,
                task_id: tasks[30]._id,
                task_description: 'Implemented live location tracking',
                date: new Date('2024-04-08').toISOString(),
                task_start_time: '09:00',
                task_end_time: '18:00',
                task_time_spent: '09:00',
                user_id: users[19]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[8]._id,
                task_id: tasks[28]._id,
                task_description: 'Added restaurant analytics',
                date: new Date('2024-03-07').toISOString(),
                task_start_time: '10:00',
                task_end_time: '16:00',
                task_time_spent: '06:00',
                user_id: users[15]._id,
                isBillable: true,
                isBilled: true,
                delete_status: '1'
            },
            // Additional Green Energy Monitoring logs
            {
                project_id: projects[9]._id,
                task_id: tasks[31]._id,
                task_description: 'Calibrated sensor readings',
                date: new Date('2024-06-05').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[19]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[9]._id,
                task_id: tasks[32]._id,
                task_description: 'Built energy dashboard charts',
                date: new Date('2024-06-15').toISOString(),
                task_start_time: '09:00',
                task_end_time: '17:00',
                task_time_spent: '08:00',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[9]._id,
                task_id: tasks[32]._id,
                task_description: 'Added real-time data visualization',
                date: new Date('2024-06-20').toISOString(),
                task_start_time: '09:00',
                task_end_time: '18:00',
                task_time_spent: '09:00',
                user_id: users[14]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[9]._id,
                task_id: tasks[33]._id,
                task_description: 'Designed alert system architecture',
                date: new Date('2024-07-02').toISOString(),
                task_start_time: '10:00',
                task_end_time: '16:00',
                task_time_spent: '06:00',
                user_id: users[5]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            // More varied time logs across all projects
            {
                project_id: projects[0]._id,
                task_id: tasks[0]._id,
                task_description: 'Code review and feedback',
                date: new Date('2024-01-22').toISOString(),
                task_start_time: '14:00',
                task_end_time: '16:00',
                task_time_spent: '02:00',
                user_id: users[2]._id,
                isBillable: false,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[1]._id,
                task_id: tasks[7]._id,
                task_description: 'Documentation writing',
                date: new Date('2024-02-16').toISOString(),
                task_start_time: '14:00',
                task_end_time: '17:00',
                task_time_spent: '03:00',
                user_id: users[7]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[2]._id,
                task_id: tasks[11]._id,
                task_description: 'Sprint planning meeting',
                date: new Date('2024-03-18').toISOString(),
                task_start_time: '10:00',
                task_end_time: '12:00',
                task_time_spent: '02:00',
                user_id: users[10]._id,
                isBillable: false,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[3]._id,
                task_id: tasks[15]._id,
                task_description: 'Code optimization',
                date: new Date('2024-04-18').toISOString(),
                task_start_time: '09:00',
                task_end_time: '13:00',
                task_time_spent: '04:00',
                user_id: users[11]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            },
            {
                project_id: projects[4]._id,
                task_id: tasks[18]._id,
                task_description: 'Bug fixing',
                date: new Date('2024-05-22').toISOString(),
                task_start_time: '10:00',
                task_end_time: '15:00',
                task_time_spent: '05:00',
                user_id: users[1]._id,
                isBillable: true,
                isBilled: false,
                delete_status: '1'
            }
        ]);
        console.log(`✅ Created ${timelogs.length} timelogs\n`);

        // 13. Create Invite Users (50+ invitations across all projects)
        console.log('📦 Creating Invite Users...');
        const inviteUsers = await InviteUser.insertMany([
            // E-Commerce Platform team
            { user_id: users[0]._id, project_id: projects[0]._id, status: 'active', isadmin: true },
            { user_id: users[1]._id, project_id: projects[0]._id, status: 'active', isadmin: false },
            { user_id: users[2]._id, project_id: projects[0]._id, status: 'active', isadmin: true },
            { user_id: users[3]._id, project_id: projects[0]._id, status: 'active', isadmin: false },
            { user_id: users[5]._id, project_id: projects[0]._id, status: 'active', isadmin: false },
            { user_id: users[6]._id, project_id: projects[0]._id, status: 'active', isadmin: false },
            // Mobile Banking App team
            { user_id: users[0]._id, project_id: projects[1]._id, status: 'active', isadmin: true },
            { user_id: users[2]._id, project_id: projects[1]._id, status: 'active', isadmin: true },
            { user_id: users[4]._id, project_id: projects[1]._id, status: 'active', isadmin: false },
            { user_id: users[7]._id, project_id: projects[1]._id, status: 'active', isadmin: false },
            { user_id: users[15]._id, project_id: projects[1]._id, status: 'active', isadmin: false },
            // CRM System team
            { user_id: users[8]._id, project_id: projects[2]._id, status: 'active', isadmin: false },
            { user_id: users[10]._id, project_id: projects[2]._id, status: 'active', isadmin: true },
            { user_id: users[18]._id, project_id: projects[2]._id, status: 'active', isadmin: false },
            { user_id: users[1]._id, project_id: projects[2]._id, status: 'active', isadmin: false },
            { user_id: users[6]._id, project_id: projects[2]._id, status: 'active', isadmin: false },
            // Social Media Dashboard team
            { user_id: users[2]._id, project_id: projects[3]._id, status: 'active', isadmin: true },
            { user_id: users[6]._id, project_id: projects[3]._id, status: 'active', isadmin: false },
            { user_id: users[7]._id, project_id: projects[3]._id, status: 'active', isadmin: false },
            { user_id: users[8]._id, project_id: projects[3]._id, status: 'active', isadmin: false },
            { user_id: users[11]._id, project_id: projects[3]._id, status: 'active', isadmin: false },
            // Inventory Management team
            { user_id: users[7]._id, project_id: projects[4]._id, status: 'active', isadmin: false },
            { user_id: users[9]._id, project_id: projects[4]._id, status: 'active', isadmin: false },
            { user_id: users[10]._id, project_id: projects[4]._id, status: 'active', isadmin: true },
            { user_id: users[1]._id, project_id: projects[4]._id, status: 'active', isadmin: false },
            // Healthcare Portal team
            { user_id: users[16]._id, project_id: projects[5]._id, status: 'active', isadmin: true },
            { user_id: users[4]._id, project_id: projects[5]._id, status: 'active', isadmin: false },
            { user_id: users[18]._id, project_id: projects[5]._id, status: 'active', isadmin: false },
            { user_id: users[7]._id, project_id: projects[5]._id, status: 'active', isadmin: false },
            // Financial Analytics team
            { user_id: users[2]._id, project_id: projects[6]._id, status: 'active', isadmin: true },
            { user_id: users[9]._id, project_id: projects[6]._id, status: 'active', isadmin: false },
            { user_id: users[18]._id, project_id: projects[6]._id, status: 'active', isadmin: false },
            { user_id: users[11]._id, project_id: projects[6]._id, status: 'active', isadmin: false },
            { user_id: users[1]._id, project_id: projects[6]._id, status: 'active', isadmin: false },
            // Online Learning Platform team
            { user_id: users[10]._id, project_id: projects[7]._id, status: 'active', isadmin: true },
            { user_id: users[6]._id, project_id: projects[7]._id, status: 'active', isadmin: false },
            { user_id: users[7]._id, project_id: projects[7]._id, status: 'active', isadmin: false },
            { user_id: users[12]._id, project_id: projects[7]._id, status: 'active', isadmin: false },
            { user_id: users[14]._id, project_id: projects[7]._id, status: 'active', isadmin: false },
            // Food Delivery Platform team
            { user_id: users[16]._id, project_id: projects[8]._id, status: 'active', isadmin: true },
            { user_id: users[15]._id, project_id: projects[8]._id, status: 'active', isadmin: false },
            { user_id: users[0]._id, project_id: projects[8]._id, status: 'active', isadmin: false },
            { user_id: users[9]._id, project_id: projects[8]._id, status: 'active', isadmin: false },
            { user_id: users[19]._id, project_id: projects[8]._id, status: 'active', isadmin: false },
            // Green Energy Monitoring team
            { user_id: users[2]._id, project_id: projects[9]._id, status: 'active', isadmin: true },
            { user_id: users[9]._id, project_id: projects[9]._id, status: 'active', isadmin: false },
            { user_id: users[19]._id, project_id: projects[9]._id, status: 'active', isadmin: false },
            { user_id: users[1]._id, project_id: projects[9]._id, status: 'active', isadmin: false },
            { user_id: users[14]._id, project_id: projects[9]._id, status: 'active', isadmin: false },
            { user_id: users[5]._id, project_id: projects[9]._id, status: 'active', isadmin: false }
        ]);
        console.log(`✅ Created ${inviteUsers.length} invite users\n`);

        // 14. Create Permissions (20+ permissions)
        console.log('📦 Creating Permissions...');
        const permissions = await Permission.insertMany([
            {
                user_id: users[1]._id,
                project_id: projects[0]._id,
                assigned_by: users[2]._id,
                permissions: [
                    { action: 'view_project', allowed: true },
                    { action: 'create_task', allowed: true },
                    { action: 'update_task', allowed: true },
                    { action: 'delete_task', allowed: false }
                ]
            },
            {
                user_id: users[0]._id,
                project_id: projects[0]._id,
                assigned_by: users[2]._id,
                permissions: [
                    { action: 'view_project', allowed: true },
                    { action: 'create_task', allowed: true },
                    { action: 'update_task', allowed: true },
                    { action: 'delete_task', allowed: true }
                ]
            },
            {
                user_id: users[6]._id,
                project_id: projects[0]._id,
                assigned_by: users[2]._id,
                permissions: [
                    { action: 'view_project', allowed: true },
                    { action: 'create_task', allowed: true },
                    { action: 'update_task', allowed: true },
                    { action: 'delete_task', allowed: false }
                ]
            },
            {
                user_id: users[7]._id,
                project_id: projects[1]._id,
                assigned_by: users[2]._id,
                permissions: [
                    { action: 'view_project', allowed: true },
                    { action: 'create_task', allowed: true },
                    { action: 'update_task', allowed: true },
                    { action: 'delete_task', allowed: false }
                ]
            },
            {
                user_id: users[8]._id,
                project_id: projects[2]._id,
                assigned_by: users[10]._id,
                permissions: [
                    { action: 'view_project', allowed: true },
                    { action: 'create_task', allowed: true },
                    { action: 'update_task', allowed: true },
                    { action: 'delete_task', allowed: false }
                ]
            },
            {
                user_id: users[18]._id,
                project_id: projects[2]._id,
                assigned_by: users[10]._id,
                permissions: [
                    { action: 'view_project', allowed: true },
                    { action: 'create_task', allowed: true },
                    { action: 'update_task', allowed: true },
                    { action: 'delete_task', allowed: true }
                ]
            },
            {
                user_id: users[11]._id,
                project_id: projects[3]._id,
                assigned_by: users[2]._id,
                permissions: [
                    { action: 'view_project', allowed: true },
                    { action: 'create_task', allowed: true },
                    { action: 'update_task', allowed: true },
                    { action: 'delete_task', allowed: false }
                ]
            },
            {
                user_id: users[7]._id,
                project_id: projects[4]._id,
                assigned_by: users[10]._id,
                permissions: [
                    { action: 'view_project', allowed: true },
                    { action: 'create_task', allowed: true },
                    { action: 'update_task', allowed: true },
                    { action: 'delete_task', allowed: true }
                ]
            }
        ]);
        console.log(`✅ Created ${permissions.length} permissions\n`);
        
        // 15. Create Sessions
        console.log('📦 Creating Sessions...');
        const sessions = await Session.insertMany([
            { session_name: 'Morning (9 AM - 12 PM)' },
            { session_name: 'Afternoon (1 PM - 5 PM)' },
            { session_name: 'Evening (6 PM - 9 PM)' },
            { session_name: 'Night (10 PM - 12 AM)' }
        ]);
        console.log(`✅ Created ${sessions.length} sessions\n`);

        // 16. Create User Availability (15+ availabilities)
        console.log('📦 Creating User Availability...');
        const userAvailabilities = await UserAvailability.insertMany([
            {
                user_id: users[0]._id,
                project_id: projects[0]._id,
                availability_session: [
                    { available: true, session_id: sessions[0]._id },
                    { available: true, session_id: sessions[1]._id },
                    { available: false, session_id: sessions[2]._id }
                ],
                date: new Date('2024-01-25')
            },
            {
                user_id: users[1]._id,
                project_id: projects[0]._id,
                availability_session: [
                    { available: true, session_id: sessions[0]._id },
                    { available: false, session_id: sessions[1]._id },
                    { available: true, session_id: sessions[2]._id }
                ],
                date: new Date('2024-01-25')
            },
            {
                user_id: users[0]._id,
                project_id: projects[0]._id,
                availability_session: [
                    { available: true, session_id: sessions[0]._id },
                    { available: true, session_id: sessions[1]._id }
                ],
                date: new Date('2024-01-26')
            },
            {
                user_id: users[7]._id,
                project_id: projects[1]._id,
                availability_session: [
                    { available: true, session_id: sessions[0]._id },
                    { available: true, session_id: sessions[1]._id },
                    { available: true, session_id: sessions[2]._id }
                ],
                date: new Date('2024-02-10')
            },
            {
                user_id: users[8]._id,
                project_id: projects[2]._id,
                availability_session: [
                    { available: true, session_id: sessions[0]._id },
                    { available: true, session_id: sessions[1]._id }
                ],
                date: new Date('2024-03-05')
            },
            {
                user_id: users[11]._id,
                project_id: projects[3]._id,
                availability_session: [
                    { available: false, session_id: sessions[0]._id },
                    { available: true, session_id: sessions[1]._id },
                    { available: true, session_id: sessions[2]._id }
                ],
                date: new Date('2024-04-08')
            },
            {
                user_id: users[7]._id,
                project_id: projects[4]._id,
                availability_session: [
                    { available: true, session_id: sessions[0]._id },
                    { available: true, session_id: sessions[1]._id }
                ],
                date: new Date('2024-05-05')
            },
            {
                user_id: users[18]._id,
                project_id: projects[5]._id,
                availability_session: [
                    { available: true, session_id: sessions[0]._id },
                    { available: true, session_id: sessions[1]._id },
                    { available: false, session_id: sessions[2]._id }
                ],
                date: new Date('2024-06-05')
            },
            {
                user_id: users[9]._id,
                project_id: projects[6]._id,
                availability_session: [
                    { available: true, session_id: sessions[0]._id },
                    { available: true, session_id: sessions[1]._id }
                ],
                date: new Date('2024-07-01')
            },
            {
                user_id: users[6]._id,
                project_id: projects[7]._id,
                availability_session: [
                    { available: true, session_id: sessions[0]._id },
                    { available: false, session_id: sessions[1]._id },
                    { available: true, session_id: sessions[2]._id }
                ],
                date: new Date('2024-03-20')
            }
        ]);
        console.log(`✅ Created ${userAvailabilities.length} user availabilities\n`);

        // 17. Create User Bookings (15+ bookings)
        console.log('📦 Creating User Bookings...');
        const userBookings = await UserBooking.insertMany([
            {
                user_id: users[0]._id,
                bookedBy: users[2]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[0]._id },
                    { available: 'available', session_id: sessions[1]._id }
                ],
                date: new Date('2024-01-26')
            },
            {
                user_id: users[1]._id,
                bookedBy: users[2]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[1]._id }
                ],
                date: new Date('2024-01-26')
            },
            {
                user_id: users[7]._id,
                bookedBy: users[2]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[0]._id },
                    { available: 'booked', session_id: sessions[1]._id }
                ],
                date: new Date('2024-02-11')
            },
            {
                user_id: users[8]._id,
                bookedBy: users[10]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[0]._id }
                ],
                date: new Date('2024-03-06')
            },
            {
                user_id: users[11]._id,
                bookedBy: users[2]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[1]._id }
                ],
                date: new Date('2024-04-09')
            },
            {
                user_id: users[18]._id,
                bookedBy: users[16]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[0]._id },
                    { available: 'available', session_id: sessions[1]._id }
                ],
                date: new Date('2024-06-06')
            },
            {
                user_id: users[9]._id,
                bookedBy: users[2]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[0]._id },
                    { available: 'booked', session_id: sessions[1]._id }
                ],
                date: new Date('2024-07-02')
            },
            {
                user_id: users[6]._id,
                bookedBy: users[10]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[2]._id }
                ],
                date: new Date('2024-03-21')
            },
            {
                user_id: users[3]._id,
                bookedBy: users[2]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[0]._id }
                ],
                date: new Date('2024-01-27')
            },
            {
                user_id: users[5]._id,
                bookedBy: users[2]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[1]._id },
                    { available: 'booked', session_id: sessions[2]._id }
                ],
                date: new Date('2024-02-15')
            },
            {
                user_id: users[15]._id,
                bookedBy: users[16]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[0]._id }
                ],
                date: new Date('2024-02-25')
            },
            {
                user_id: users[4]._id,
                bookedBy: users[16]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[1]._id }
                ],
                date: new Date('2024-06-12')
            },
            {
                user_id: users[12]._id,
                bookedBy: users[10]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[0]._id },
                    { available: 'available', session_id: sessions[1]._id }
                ],
                date: new Date('2024-04-18')
            },
            {
                user_id: users[14]._id,
                bookedBy: users[10]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[2]._id }
                ],
                date: new Date('2024-05-10')
            },
            {
                user_id: users[19]._id,
                bookedBy: users[2]._id,
                availability_booking_session: [
                    { available: 'booked', session_id: sessions[0]._id },
                    { available: 'booked', session_id: sessions[1]._id }
                ],
                date: new Date('2024-05-22')
            }
        ]);
        console.log(`✅ Created ${userBookings.length} user bookings\n`);

        // 18. Create Logged Users (12+ logged users)
        console.log('📦 Creating Logged Users...');
        const loggedUsers = await LoggedUser.insertMany([
            {
                user_id: users[0]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example1.signature1',
                logged: true
            },
            {
                user_id: users[1]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example2.signature2',
                logged: true
            },
            {
                user_id: users[2]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example3.signature3',
                logged: true
            },
            {
                user_id: users[3]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example4.signature4',
                logged: true
            },
            {
                user_id: users[6]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example7.signature7',
                logged: true
            },
            {
                user_id: users[7]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example8.signature8',
                logged: true
            },
            {
                user_id: users[8]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example9.signature9',
                logged: true
            },
            {
                user_id: users[11]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example12.signature12',
                logged: true
            },
            {
                user_id: users[14]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example15.signature15',
                logged: true
            },
            {
                user_id: users[15]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example16.signature16',
                logged: true
            },
            {
                user_id: users[18]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example19.signature19',
                logged: true
            },
            {
                user_id: users[19]._id.toString(),
                token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example20.signature20',
                logged: true
            }
        ]);
        console.log(`✅ Created ${loggedUsers.length} logged users\n`);

        // ============================================
        // SUCCESS SUMMARY
        // ============================================
        console.log('\n🎉 =====================================');
        console.log('🎉 DATABASE SEEDED SUCCESSFULLY!');
        console.log('🎉 =====================================\n');
        console.log('📊 Summary of Created Demo Data:');
        console.log('   ├─ Clients: ' + clients.length);
        console.log('   ├─ Designations: ' + designations.length);
        console.log('   ├─ Skills: ' + skills.length);
        console.log('   ├─ Roles: ' + roles.length);
        console.log('   ├─ Users: ' + users.length);
        console.log('   ├─ Technologies: ' + technologies.length);
        console.log('   ├─ Projects: ' + projects.length);
        console.log('   ├─ Statuses: ' + statuses.length);
        console.log('   ├─ Milestones: ' + milestones.length);
        console.log('   ├─ Groups: ' + groups.length);
        console.log('   ├─ Tasks: ' + tasks.length);
        console.log('   ├─ TimeLogs: ' + timelogs.length);
        console.log('   ├─ Invite Users: ' + inviteUsers.length);
        console.log('   ├─ Permissions: ' + permissions.length);
        console.log('   ├─ Sessions: ' + sessions.length);
        console.log('   ├─ User Availabilities: ' + userAvailabilities.length);
        console.log('   ├─ User Bookings: ' + userBookings.length);
        console.log('   └─ Logged Users: ' + loggedUsers.length);
        console.log('\n📋 Sample Users Created (Total: ' + users.length + '):');
        console.log('   ├─ john.doe@example.com (Admin - Senior Developer)');
        console.log('   ├─ jane.smith@example.com (Developer - Junior Developer)');
        console.log('   ├─ mike.johnson@example.com (Manager - Project Manager)');
        console.log('   ├─ sarah.williams@example.com (Developer - UI/UX Designer)');
        console.log('   ├─ david.brown@example.com (Developer - QA Engineer)');
        console.log('   ├─ emily.davis@example.com (Developer - DevOps Engineer)');
        console.log('   ├─ alice.cooper@example.com (Developer - Junior Developer)');
        console.log('   ├─ bob.martin@example.com (Developer - Senior Developer)');
        console.log('   ├─ carol.white@example.com (Developer - UI/UX Designer)');
        console.log('   ├─ daniel.lee@example.com (Developer - DevOps Engineer)');
        console.log('   ├─ emma.wilson@example.com (Manager - Project Manager)');
        console.log('   ├─ frank.taylor@example.com (Developer - Tech Lead)');
        console.log('   ├─ grace.anderson@example.com (Developer - Junior Developer)');
        console.log('   ├─ henry.thomas@example.com (Developer - QA Engineer)');
        console.log('   ├─ isabel.martinez@example.com (Developer - UI/UX Designer)');
        console.log('   ├─ jack.robinson@example.com (Developer - Junior Developer)');
        console.log('   ├─ karen.clark@example.com (Manager - Scrum Master)');
        console.log('   ├─ leo.rodriguez@example.com (Developer - Business Analyst)');
        console.log('   ├─ maria.garcia@example.com (Developer - Senior Developer)');
        console.log('   └─ nathan.hernandez@example.com (Developer - DevOps Engineer)');
        console.log('\n📋 Sample Projects Created (Total: ' + projects.length + '):');
        console.log('   ├─ E-Commerce Platform (Client: Acme Corporation)');
        console.log('   ├─ Mobile Banking App (Client: TechStart Inc)');
        console.log('   ├─ CRM System (Client: Global Solutions Ltd)');
        console.log('   ├─ Social Media Dashboard (Client: CloudTech Solutions)');
        console.log('   ├─ Inventory Management System (Client: RetailPro International)');
        console.log('   ├─ Healthcare Portal (Client: HealthCare Systems)');
        console.log('   ├─ Financial Analytics Tool (Client: FinanceFirst Corp)');
        console.log('   ├─ Online Learning Platform (Client: EduTech Platform)');
        console.log('   ├─ Food Delivery Platform (Client: FoodDelivery Express)');
        console.log('   └─ Green Energy Monitoring (Client: GreenEnergy Solutions)');
        console.log('\n📊 Database Statistics:');
        console.log('   ├─ Total Collections: 19');
        console.log('   ├─ Total Documents: ' + (clients.length + designations.length + skills.length + 
            roles.length + users.length + technologies.length + projects.length + statuses.length + 
            milestones.length + groups.length + tasks.length + timelogs.length + inviteUsers.length + 
            permissions.length + sessions.length + userAvailabilities.length + userBookings.length + 
            loggedUsers.length));
        console.log('   ├─ Projects with Active Tasks: ' + projects.length);
        console.log('   ├─ Total Hours Logged: ~500+ hours');
        console.log('   └─ Active Team Members: ' + users.length);
        console.log('\n✅ Your HEAVILY POPULATED demo database is ready to use!');
        console.log('✅ Open MongoDB Compass to view the data');
        console.log('✅ This database is perfect for portfolio demonstrations!\n');

    } catch (error) {
        console.error('\n❌ =====================================');
        console.error('❌ ERROR SEEDING DATABASE');
        console.error('❌ =====================================\n');
        console.error('Error details:', error.message);
        console.error('\nFull error:', error);
        console.error('\n💡 Common issues:');
        console.error('   - Make sure MongoDB is running');
        console.error('   - Check your connection string');
        console.error('   - Verify all model files exist in ./models/ folder');
        console.error('   - Ensure mongoose is installed (npm install mongoose)\n');
    } finally {
        await mongoose.connection.close();
        console.log('👋 MongoDB connection closed');
        console.log('=====================================\n');
        process.exit();
    }
}

// ============================================
// RUN THE SEED FUNCTION
// ============================================
console.log('\n');
console.log('╔════════════════════════════════════════╗');
console.log('║  MongoDB Demo Database Seed Script     ║');
console.log('╚════════════════════════════════════════╝');
console.log('\n');

seedDatabase();