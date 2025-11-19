const mongoose = require('mongoose')
const Schema = mongoose.Schema

const StatusesSchema = new Schema({

    task_status: { type: String, require: true, index: true},
    text_color: { type: String },
    bg_color: { type: String }
},
    { timestamps: true }
)

const Statuses = mongoose.model('Statuses', StatusesSchema);
module.exports = Statuses;
