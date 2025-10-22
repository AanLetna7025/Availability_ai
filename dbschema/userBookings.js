const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const UserBookingSchema = new Schema({
    user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    
    bookedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

    availability_booking_session: [
        {
            available: { type: String, enum: ['available', 'booked'], require: true, default: 'available' }, 
            session_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Session' }
        }
    ],
    
    date: Date,
});

const UserBookings = mongoose.model('user_bookings', UserBookingSchema);
module.exports = UserBookings;
