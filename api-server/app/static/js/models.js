/**
 * Exports TodoModel, TodoCollection.
 * Expects Backbone
 * */

var TodoModel = Backbone.Model.extend({
  idAttribute: 'task_id',
  urlRoot: '/tasks'
});

var TodoCollection = Backbone.Collection.extend({
  model: TodoModel,
  url: '/tasks',
  parse: function (response) {
    var self = this;
    response.tasks.forEach(function (item) {
      item.completed = false;
      self.push(item)
    })
    return this.models;
  }
});
