const mongoose = require('mongoose')
const Schema = mongoose.Schema

const MilestoneSchema = new Schema({
    project_id: { type: Schema.Types.ObjectId, ref: 'Project', require: true, index: true },

    title: { type: String, require: true },

    description: { type: String },

    status: { type: String, enum: ['0', '1'], require: true, default: '1' },

    created_by: { type: mongoose.Schema.Types.ObjectId, ref: 'User', require: true, index: true },

    created_date: { type: Date, default: () => new Date().toISOString() },

    is_current_milestone: { type: Boolean, default: false, index: true },

    start_date: { type: Date },

    end_date: { type: Date },

    milestone_created_by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

},
    {
        timestamps: true
    }
)

const Milestone = mongoose.model('milestone', MilestoneSchema);
module.exports = Milestone;
