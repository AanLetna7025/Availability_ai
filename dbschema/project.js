const mongoose = require('mongoose');
const Schema = mongoose.Schema

const ProjectSchema = new Schema({
    name: String,
    description: String,
    client: { type: Schema.ObjectId, ref: 'Client' },
    start_date: Date,
    end_date: Date,
    platform: { type: String, default: 'web' },
    status: { type: String, default: 'ongoing' },
    requirement: [{
        title: { type: String, required: true },
        createdAt: { type: Date, default: null },
        updatedAt: { type: Date, default: null },
        description: { type: String, default: null },
        status: Boolean,
        notes: [{
            title: { type: String, required: true },
            createdAt: { type: Date, default: null },
            updatedAt: { type: Date, default: null },
            description: { type: String, default: null },
            status: Boolean
        }]
    }],
    technologies: {
        server: [{
            techId: { type: Schema.ObjectId, ref: 'Technology' },
            version: String,
            note: String,
            reason: String,
            status: Boolean
        }],
        client: [{
            techId: { type: Schema.ObjectId, ref: 'Technology' },
            version: String,
            note: String,
            reason: String,
            status: Boolean
        }]
    },
    issues: [
        {
            title: String,
            answer: String,
        }
    ],
}, {
    toJSON: { virtuals: true }, // So `res.json()` and other `JSON.stringify()` functions include virtuals
    toObject: { virtuals: true } // So `console.log()` and other functions that use `toObject()` include virtuals
});


ProjectSchema.virtual('inviteuser', {
    ref: 'invite_users',
    localField: '_id',
    foreignField: 'project_id'
});

ProjectSchema.virtual('availability', {
    ref: 'user_availability_calenders',
    localField: '_id',
    foreignField: 'project_id'
});
ProjectSchema.virtual('project_documents', {
    ref: 'project_documents',
    localField: '_id',
    foreignField: 'project_id'
});


const Project = mongoose.model('Project', ProjectSchema);

module.exports = Project;
