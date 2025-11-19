const mongoose = require('mongoose')
const Schema = mongoose.Schema

const TimelogSchema = new Schema({

    project_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Project', require: true, index: true },

    task_id: { type: mongoose.Schema.Types.ObjectId, default: null, ref: 'Task', index: true },

    task_description: { type: String },

    date: { type: String, default: new Date(Date.now()).toISOString() },

    task_start_time: { type: String, default: null },

    task_end_time: { type: String, default: null },

    task_time_spent: { type: String },

    user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', require: true, index: true },

    isBillable: { type: Boolean, default: false },

    isBilled: { type: Boolean, default: false },

    delete_status: { type: String, enum: ['0', '1'], require: true, default: '1' },
},
    { timestamps: true }
)

const Timelog = mongoose.model('TimeLog', TimelogSchema);
module.exports = Timelog;
