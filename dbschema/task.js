const mongoose = require('mongoose')
const Schema = mongoose.Schema
const Milestone = require('./milestone')

const TaskSchema = new Schema({
    project_id: { type: Schema.Types.ObjectId, ref: 'Project', require: true, index: true },

    milestone_id: { type: Schema.Types.ObjectId, ref: 'milestone', require: false, default: null, index: true },

    parent_id: { type: Schema.Types.ObjectId, default: null, ref: 'Task' },

    group_id: { type: Schema.Types.ObjectId, default: null, ref: 'Group', index: true },

    task_name: { type: String, require: true },

    task_description: { type: String, default: null },

    // task_status: {type: String, default: 'Todo'},

    task_status: { type: Schema.Types.ObjectId, default: null, ref: 'Statuses', index: true },

    status_name: { type: String, default: 'NEW' },

    task_priority: { type: String, default: null },

    estimate: { type: String },
    // estimate: {hour: 10, minute: 0}

    task_start_date: { type: Date, default: null },

    task_end_date: { type: Date, default: null, index: true },

    assigned_by: { type: Schema.Types.ObjectId, default: null, ref: 'User', index: true },

    assigned_to: [{ type: Schema.Types.ObjectId, default: null, ref: 'User', index: true }],

    task_created_by: { type: Schema.Types.ObjectId, ref: 'User', index: true },

    comments: [{
        comment: {
            type: String, default: null
        },
        replies: [{
            reply: {
                type: String, default: null
            }
        }],
        user_id: {
            type: Schema.Types.ObjectId, ref: 'User', require: true
        },
        is_reply: {
            type: Boolean, default: false
        },
        created_At: {
            type: Date, default: Date.now()
        }
    }],

    is_task_finished: { type: Boolean, required: false, default: false, index: true },

    task_logged_time: { type: String, default: "00:00" }
},
    { timestamps: true }
)

const Task = mongoose.model('Task', TaskSchema);
module.exports = Task;
