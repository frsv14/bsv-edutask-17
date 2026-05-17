describe('Testing todo list functionality', () => {
  let uid 
  let name 
  let email 

  before(function () {
    // create user from fixture
    cy.fixture('user.json')
      .then((user) => {
        cy.request({
          method: 'POST',
          url: 'http://localhost:5000/users/create',
          form: true,
          body: user
        }).then((response) => {
          uid = response.body._id.$oid
          name = user.firstName + ' ' + user.lastName
          email = user.email
        })
      })
  })

  beforeEach(function () {
    // enter main page after each
    cy.visit('http://localhost:3000')

    // login
    cy.contains('div', 'Email Address')
      .find('input[type=text]')
      .type(email)
    cy.get('form')
      .submit()

    // create task
    cy.get('#title')
      .type('Learn Cypress')
    cy.get('#url')
      .type('abcdef')
    cy.get('form.submit-form.bordered')
      .submit()
  })

  it('create a new todo item', () => { 

    // click on task to open detail
    cy.contains('.title-overlay', 'Learn Cypress')
      .click()

    // add a todo item
    cy.get('input[placeholder="Add a new todo item"]')
      .type('Watch the video')
    cy.get('form.inline-form input[type=submit]')
      .click()

    // assert the todo item was added
    cy.get('.todo-item')
      .should('contain.text', 'Watch the video')
  })

  it('disable add button when todo description is empty', () => {

    cy.contains('.title-overlay', 'Learn Cypress')
      .click()

    cy.get('form.inline-form input[type=submit]')
      .should('be.disabled')

    cy.get('input[placeholder="Add a new todo item"]')
      .type('Now enabled')

    cy.get('form.inline-form input[type=submit]')
      .should('not.be.disabled')
  })

  it('toggle a todo item as done', () => {

    // click task to open detail
    cy.contains('.title-overlay', 'Learn Cypress')
      .click()

    // add todo item
    cy.get('input[placeholder="Add a new todo item"]')
      .type('Practice testing')
    cy.get('form.inline-form input[type=submit]')
      .click()

    // toggle todo item as done clicking checker
    cy.get('.todo-item .checker')
      .first()
      .click()

    // assert todo item is marked as done
    cy.get('.todo-item .checker')
      .first()
      .should('have.class', 'checked')
  })

  it('toggle a todo item back to active', () => {

  // click task to open detail
  cy.contains('.title-overlay', 'Learn Cypress')
    .click()

  // add todo item
  cy.get('input[placeholder="Add a new todo item"]')
    .type('Practice testing')
  cy.get('form.inline-form input[type=submit]')
    .click()

  // toggle todo item as done clicking checker
  cy.get('.todo-item .checker')
    .first()
    .click()

  // assert todo item is marked as done
  cy.get('.todo-item .checker')
    .first()
    .should('have.class', 'checked')


  // toggle todo item back to active
  cy.get('.todo-item .checker')
    .first()
    .click()

  // assert todo item is back to active
  cy.get('.todo-item .checker')
    .first()
    .should('have.class', 'unchecked')


  })

  it('delete a todo item', () => {

    // click task to open detail
    cy.get('.container-element img').first().click()

    // add todo item
    cy.get('input[placeholder="Add a new todo item"]')
      .type('Item to delete')
    cy.get('form.inline-form input[type=submit]')
      .click()

    // wait for item to appear then delete
    cy.contains('.todo-item', 'Item to delete')
      .find(".remover")
      .click()
      .click() // idk why this works but it works

    // assert todo item was deleted
    cy.contains('.todo-item', 'Item to delete')
      .should('not.exist')
  })

  afterEach(function () {
    // Todo DB cleanup
    cy.request({
      method: 'GET',
      url: `http://localhost:5000/tasks/ofuser/${uid}`
    }).then((response) => {
      const tasks = response.body || []
      cy.wrap(tasks).each((task) => {
        const taskId = task._id?.$oid || task._id
        if (taskId) {
          cy.request({
            method: 'DELETE',
            url: `http://localhost:5000/tasks/byid/${taskId}`
          })
        }
      })
    })
  })

  after(function () {
    //User DB cleanup
    cy.request({
      method: 'DELETE',
      url: `http://localhost:5000/users/${uid}`
    }).then((response) => {
      cy.log(response.body)
    })
  })
})

