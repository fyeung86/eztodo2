/**
 * Expects: Backbone, jQuery, underscore, TodoCollection.
 * Exports: TodoView, AppView
 */

var TodoView = Backbone.View.extend({
  tagName: 'li',
  template: _.template($('#item-template').html()),
  render: function(){
    this.$el.html(this.template(this.model.toJSON()));
    this.input = this.$('.updateAction');
    return this;
  },
  initialize: function(){
    this.model.on('change', this.render, this);
    this.model.on('destroy', this.remove, this);
  },
  events: {
    'dblclick .action' : 'edit',
    'keypress .updateAction' : 'updateOnEnter',
    'blur .updateAction' : 'close',
    'click .toggle': 'toggleCompleted',
    'click .close': 'destroy',
    'click .check': 'check'
  },
  edit: function(){
    this.$el.addClass('editing');
    this.input.focus();
  },
  close: function(){
    var value = this.input.val().trim();
    if(value) {
      this.model.save({action: value});
    }
    this.$el.removeClass('editing');
  },
  updateOnEnter: function(e){
    if(e.which == 13){
      this.close();
    }
  },
  destroy: function () {
      this.model.destroy();
  },
  check: function () {
      this.$el.toggleClass('checked');
  }
});

var AppView = Backbone.View.extend({
  el: '#myDIV',
  initialize: function(){
    var todoList = this.todoList = new TodoCollection();
    this.todoList.fetch({
      success: function (item) {
        todoList.models.forEach(function (item) {
          console.log(item);
          var view = new TodoView({model: item});
          $('#myUL').append(view.render().el);
        })
      }
    })
    this.render();
  },
  events: {
    'click .addBtn': 'create'
  },
  create: function () {
    var action = $('#taskInput').val();
    if (action === '') {
      return;
    } 
    this.todoList.create({'action': action}, {
      success: function (model) {
        model.completed = false;
        var view = new TodoView({model: model});
        $('#myUL').append(view.render().el);
        $('#taskInput').val('');
      }
    });
  }
});
