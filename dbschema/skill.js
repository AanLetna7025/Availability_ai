const mongoose = require('mongoose');
const Schema = mongoose.Schema;
//mongoose.set('debug', true);
const SkillsSchema = new Schema({
    name: String,
    status:String
});
const Skill = mongoose.model('Skill', SkillsSchema);

module.exports = Skill;
