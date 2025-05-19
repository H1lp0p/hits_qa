import { test, expect } from '@playwright/test';

//test_db -> backend (with test) -> vite -> npx playwright test --ui

const new_unique = `${(new Date().toISOString())}`

test.beforeEach(async ({page}) =>{
  await fetch("http://localhost:8000/test/clear", {
    method: "POST"
  });
  await page.goto('http://localhost:5173/');

})

const create_task = async (page, name) => {
  await page.getByRole('textbox', { name: 'name' }).click();
  await page.getByRole('textbox', { name: 'name' }).fill(name);
  await page.getByRole('button', { name: 'Create' }).click();

  // ждет завершения сетевых запросов - в данном случае обновления страницы после создания нового таска
  await page.waitForLoadState("networkidle"); 
}


test('try to create with 3 symbs', async ({ page }) => {
  await page.getByRole('textbox', { name: 'name' }).click();
  await page.getByRole('textbox', { name: 'name' }).fill('123');
  await expect(page.getByRole('button', { name: 'Create' })).toBeDisabled();
})

test('create with 4 symbs', async ({ page }) => {
  await page.getByRole('textbox', { name: 'name' }).click();
  await page.getByRole('textbox', { name: 'name' }).fill(`${new_unique} 1234`);
  await page.getByRole('button', { name: 'Create' }).click();
  await expect(page.getByText(`${new_unique} 1234`)).toBeVisible();
})

test('checkink edit all attrs + soon task color', async ({ page }) => {
  const new_name = `${new_unique} task for editing`

  const nowInUTC7 = new Date(
    new Date().toLocaleString('en-US', {timeZone: 'Asia/Novosibirsk'})
  );
  let nextDay = new Date(nowInUTC7);
  nextDay.setDate(nowInUTC7.getDate() + 1);
  const formatter = new Intl.DateTimeFormat('fr-CA', {
    timeZone: 'Asia/Novosibirsk',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
  const next_day_string = formatter.format(nextDay);

  await create_task(page, new_name)
  
  await page.getByText(new_name).locator("..").click();
  await page.getByRole('textbox', { name: 'name' }).click();
  await page.getByRole('textbox', { name: 'name' }).fill(`${new_name} edited`);
  await page.getByRole('textbox', { name: 'description' }).click();
  await page.getByRole('textbox', { name: 'description' }).fill('description');
  await page.getByRole('combobox').selectOption('0');
  await page.locator('input[name="deadline"]').fill(`${next_day_string}`);
  await page.getByRole('button', { name: 'Edit' }).click();

  await expect(page.getByText(`${new_name} edited`).locator("..")).toContainText(`to ${next_day_string}`);

  await expect(page.getByText(`${new_name} edited`).locator("..")).toHaveCSS("background-color", "rgb(211, 127, 53)")
  await expect(page.getByText(`${new_name} edited`).locator("..")).toContainText('active');
  await page.getByText(new_name).locator("..").click();
})

test('checkink overdue status and color', async ({ page }) => {
  const new_name = `${new_unique} task for editing`

  const nowInUTC7 = new Date(
    new Date().toLocaleString('en-US', {timeZone: 'Asia/Novosibirsk'})
  );
  let prewDay = new Date(nowInUTC7);
  prewDay.setDate(nowInUTC7.getDate() - 1);
  const formatter = new Intl.DateTimeFormat('fr-CA', {
    timeZone: 'Asia/Novosibirsk',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
  const prew_day_string = formatter.format(prewDay);

  await create_task(page, new_name)
  
  await page.getByText(new_name).locator("..").click();
  await page.getByRole('textbox', { name: 'name' }).click();
  await page.getByRole('textbox', { name: 'name' }).fill(`${new_name} edited`);
  await page.getByRole('textbox', { name: 'description' }).click();
  await page.getByRole('textbox', { name: 'description' }).fill('description');
  await page.getByRole('combobox').selectOption('0');
  await page.locator('input[name="deadline"]').fill(`${prew_day_string}`);
  await page.getByRole('button', { name: 'Edit' }).click();

  await expect(page.getByText(`${new_name} edited`).locator("..")).toContainText(`to ${prew_day_string}`);

  await expect(page.getByText(`${new_name} edited`).locator("..")).toHaveCSS("background-color", "rgb(194, 62, 33)")
  await expect(page.getByText(`${new_name} edited`).locator("..")).toContainText('overdue');
  await page.getByText(new_name).locator("..").click();
})

test('checkink late status and color', async ({ page }) => {
  const new_name = `${new_unique} task for editing`

  const nowInUTC7 = new Date(
    new Date().toLocaleString('en-US', {timeZone: 'Asia/Novosibirsk'})
  );
  let prewDay = new Date(nowInUTC7);
  prewDay.setDate(nowInUTC7.getDate() - 1);
  const formatter = new Intl.DateTimeFormat('fr-CA', {
    timeZone: 'Asia/Novosibirsk',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
  const prew_day_string = formatter.format(prewDay);

  await create_task(page, new_name)
  
  await page.getByText(new_name).locator("..").click();
  await page.getByRole('textbox', { name: 'name' }).click();
  await page.getByRole('textbox', { name: 'name' }).fill(`${new_name} edited`);
  await page.getByRole('textbox', { name: 'description' }).click();
  await page.getByRole('textbox', { name: 'description' }).fill('description');
  await page.getByRole('combobox').selectOption('0');
  await page.locator('input[name="deadline"]').fill(`${prew_day_string}`);
  await page.getByRole('checkbox', { name: 'Done?' }).check();
  await page.getByRole('button', { name: 'Edit' }).click();

  await expect(page.getByText(`${new_name} edited`).locator("..")).toContainText(`to ${prew_day_string}`);

  await expect(page.getByText(`${new_name} edited`).locator("..")).toHaveCSS("background-color", "rgb(136, 185, 142)")
  await expect(page.getByText(`${new_name} edited`).locator("..")).toContainText('late');
  await page.getByText(new_name).locator("..").click();
})

test('checkink complete status and color', async ({ page }) => {
  const new_name = `${new_unique} task for editing`

  const nowInUTC7 = new Date(
    new Date().toLocaleString('en-US', {timeZone: 'Asia/Novosibirsk'})
  );
  let prewDay = new Date(nowInUTC7);
  prewDay.setDate(nowInUTC7.getDate() + 10);
  const formatter = new Intl.DateTimeFormat('fr-CA', {
    timeZone: 'Asia/Novosibirsk',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
  const prew_day_string = formatter.format(prewDay);

  await create_task(page, new_name)
  
  await page.getByText(new_name).locator("..").click();
  await page.getByRole('textbox', { name: 'name' }).click();
  await page.getByRole('textbox', { name: 'name' }).fill(`${new_name} edited`);
  await page.getByRole('textbox', { name: 'description' }).click();
  await page.getByRole('textbox', { name: 'description' }).fill('description');
  await page.getByRole('combobox').selectOption('0');
  await page.locator('input[name="deadline"]').fill(`${prew_day_string}`);
  await page.getByRole('checkbox', { name: 'Done?' }).check();
  await page.getByRole('button', { name: 'Edit' }).click();

  await expect(page.getByText(`${new_name} edited`).locator("..")).toContainText(`to ${prew_day_string}`);

  await expect(page.getByText(`${new_name} edited`).locator("..")).toHaveCSS("background-color", "rgb(136, 185, 142)")
  await expect(page.getByText(`${new_name} edited`).locator("..")).toContainText('complete');
  await page.getByText(new_name).locator("..").click();
})

// test('checking OVERDUE + late task color', async ({ page }) => {
//   const new_name = `${new_unique} 1234`

//   await create_task(page, new_name)

//   await page.getByText(new_name).locator("..").click();
//   await page.locator('input[name="deadline"]').fill('2025-05-01');
//   await page.getByRole('button', { name: 'Edit' }).click();

//   await expect(page.getByText(new_name).locator("..")).toHaveCSS("background-color", "rgb(194, 62, 33)")
//   await expect(page.getByText(new_name).locator("..")).toContainText('overdue');
//   await page.getByText(new_name).locator("..").click();
// })

// статусы и цвет красный

test('checking macros !1', async ({ page }) => {
  const new_name = `${new_unique} macro !1`;
  await create_task(page, new_name)
  await expect(page.getByText(`${new_unique} macro`).locator("..")).toContainText('critical');
})


test('checking macro !before 01.01.2025', async ({ page }) => {
  const new_name = `${new_unique} deadline !before 01.01.2025`;
  await create_task(page, new_name)
  await expect(page.getByText(`${new_unique} deadline`).locator("..")).toContainText('to 2025-01-01');
})

test('checking two macroses', async ({ page }) => {
  const new_name = `${new_unique} double !4 !before 02.02.2025`;
  await create_task(page, new_name)
  await expect(page.getByText(`${new_unique} double`).locator("..")).toContainText('low');
  await expect(page.getByText(`${new_unique} double`).locator("..")).toContainText('to 2025-02-02');
})

test('checking inputs priority', async ({ page }) => {
  await page.getByRole('textbox', { name: 'name' }).click();
  await page.getByRole('textbox', { name: 'name' }).fill(`${new_unique} with priority !4 !before 02.02.2025`);
  await page.getByRole('combobox').selectOption('2');
  await page.locator('input[name="deadline"]').fill('2025-01-01');
  await page.getByRole('button', { name: 'Create' }).click();

  await page.waitForLoadState("networkidle"); 

  await expect(page.getByText(`${new_unique} with priority`).locator("..")).toContainText('medium');
  await expect(page.getByText(`${new_unique} with priority`).locator("..")).toContainText('to 2025-01-01');
})


test("checking sorting by priority asc", async ({page}) => {

  const new_name_low = `${new_unique} lowpri !4`

  await create_task(page, new_name_low);

  await page.getByRole('button', { name: 'desc' }).click();

  await expect(page.getByRole('button', {name: 'asc'})).toBeAttached();
  await expect(page.locator('#task_list div').first()).toContainText('low');
})

test("checking sorting by priority desc", async ({page}) => {

  const new_name_low = `${new_unique} criticalpri !1`

  await create_task(page, new_name_low);

  //await page.getByRole('button', { name: 'desc' }).click();

  await expect(page.getByRole('button', {name: 'desc'})).toBeAttached();
  await expect(page.locator('#task_list div').first()).toContainText('critical');
})

  //checking sorting by deadline
test("checking sorting by deadline desc", async ({page}) => {
  const new_name_low = `${new_unique} deadline highest !before 01.01.2030`

  await create_task(page, new_name_low);

  await page.getByRole('button', { name: 'priority' }).click();
  await expect(page.getByRole('button', {name: "deadline"})).toBeAttached();
  await expect(page.locator('#task_list div').first()).toContainText("to 2030-01-01");
})

test("checking sorting by deadline asc", async ({page}) => {
  const new_name_low = `${new_unique} deadline lowest`

  await create_task(page, new_name_low);

  
  await page.getByRole('button', { name: 'desc' }).click();
  await page.getByRole('button', { name: 'priority' }).click();

  await expect(page.getByRole('button', {name: 'asc'})).toBeAttached();
  await expect(page.getByRole('button', {name: "deadline"})).toBeAttached();
  await expect(page.locator('#task_list div').first()).not.toContainText("to ");
})

test("checking deleting", async ({page}) => {

  const new_name = `${new_unique} task to delete`

  await create_task(page, new_name)
  await page.getByText(new_name).locator("..").click();

  await page.getByRole('button', { name: 'Delete' }).click();
  await expect(page.getByText(new_name)).toHaveCount(0);
})