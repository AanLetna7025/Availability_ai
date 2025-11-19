const mongoose = require('mongoose')
const Schema = mongoose.Schema
const Milestone = require('./milestone')

const TaskUpdateHistorySchema = new Schema({
    oldTask_id: { type: Schema.Types.ObjectId },

    project_id: { type: Schema.Types.ObjectId },

    milestone_id: { type: Schema.Types.ObjectId },

    parent_id: { type: Schema.Types.ObjectId},

    group_id: { type: Schema.Types.ObjectId},

    task_name: { type: String, require: true },

    task_description: { type: String, default: null },

    task_status: {type: String, default: 'todo'},

    status_id: { type: Schema.Types.ObjectId},

    status_name: { type: String, default: 'NEW' },

    task_priority: { type: String, default: null},

    estimate: { type: Number, default: 0 },
    // estimate: {hour: 10, minute: 0}

    task_start_date: { type: Date, default: null },

    task_end_date: { type: Date, default: null },

    assigned_by: { type: Schema.Types.ObjectId},

    assigned_to: [{ type: Schema.Types.ObjectId}],

    comments: [{
        comment: {
            type: String, default: null
        },
        user_id: {
            type: Schema.Types.ObjectId
        },
        created_At: {
            type: Date, default: Date.now()
        }
    }],
    updated_fields: [{ type: Object}]
},
{ timestamps: true }
)

const TaskUpdateHistory = mongoose.model('TaskUpdateHistory', TaskUpdateHistorySchema);
module.exports = TaskUpdateHistory;
