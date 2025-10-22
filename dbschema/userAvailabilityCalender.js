const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const UserAvailabilityCalenderSchema = new Schema({
    user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    project_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Project' },
    // availability_session: [{ session_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Session' } }],
    // availability_session: [{start_time: {type: Date}, end_time: {type: Date}, estimated_hrs: {type: Number}}],
    availability_session: [{ available: { type: Boolean, default: true }, session_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Session' } }],
    // availability_session: [{start_time: {type: Date}, end_time: {type: Date}}],
    date: Date,
});

const UserAvailabilityCalender = mongoose.model('user_availability_calenders', UserAvailabilityCalenderSchema);
module.exports = UserAvailabilityCalender;
