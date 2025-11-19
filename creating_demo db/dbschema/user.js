const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const UserSchema = new Schema(
  {
    first_name: String,
    last_name: String,
    email: { type: String, unique: true, index: true },
    password: String,
    roles: [{ type: Schema.ObjectId, ref: "Role", index: true }],
    designation: { type: Schema.ObjectId, ref: "Designation", index: true },
    resetPasswordToken: String,
    skills: [{ type: Schema.ObjectId, ref: "Skill" }],
    tw_user_id: { type: String, required: false, default: null },
    skype_id: { type: String, required: false, default: "NA" },
    current_status: {
      type: String,
      enum: ["online", "offline"],
      default: "offline",
    },
    profile_picture: {
      type: String,
      required: false,
      default: null,
    },
    phone_number: {
      type: String,
      required: false,
      default: null,
    },
  },
  {
    toJSON: { virtuals: true }, // So `res.json()` and other `JSON.stringify()` functions include virtuals
    toObject: { virtuals: true }, // So `console.log()` and other functions that use `toObject()` include virtuals
  }
);

UserSchema.virtual("availability", {
  ref: "user_availability_calenders",
  localField: "_id",
  foreignField: "user_id",
});

UserSchema.virtual("bookings", {
  ref: "user_bookings",
  localField: "_id",
  foreignField: "user_id",
});

const User = mongoose.model("User", UserSchema);

module.exports = User;
