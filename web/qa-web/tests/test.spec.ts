import { test, expect } from '@playwright/test';

//test_db -> backend (with test) -> vite -> npx playwright test --ui

test('test', async ({ page }) => {
  await page.goto('http://localhost:5173/');

  const new_unique = `${(new Date()).getMilliseconds() % 10000}`

  //create with 3 symbs
  await test.step("try to create with 3 symbs", async () => {
    await page.getByRole('textbox', { name: 'name' }).click();
    await page.getByRole('textbox', { name: 'name' }).fill('123');
    await expect(page.getByRole('button', { name: 'Create' })).toBeDisabled();
  })
  

  //create with 4 symbs
  await test.step("create with 4 symbs", async () => {
    await page.getByRole('textbox', { name: 'name' }).click();
    await page.getByRole('textbox', { name: 'name' }).fill(`${new_unique} 1234`);
    await page.getByRole('button', { name: 'Create' }).click();
    await expect(page.getByText(`${new_unique} 1234`)).toBeVisible();
  })

  //edit all attrs
  await test.step("edit all attrs", async () => {
    await page.getByText(`${new_unique} 1234`).locator("..").click();
    await page.getByRole('textbox', { name: 'name' }).click();
    await page.getByRole('textbox', { name: 'name' }).fill(`${new_unique} 1234 edited`);
    await page.getByRole('textbox', { name: 'description' }).click();
    await page.getByRole('textbox', { name: 'description' }).fill('description');
    await page.getByRole('combobox').selectOption('0');
    await page.locator('input[name="deadline"]').fill('2025-05-15');
    await page.getByRole('button', { name: 'Edit' }).click();
    await expect(page.getByText(`${new_unique} 1234 edited`).locator("..")).toContainText("to 2025-05-15");

    await expect(page.getByText(`${new_unique} 1234 edited`).locator("..")).toHaveCSS("background-color", "rgb(211, 127, 53)")
    await expect(page.getByText(`${new_unique} 1234 edited`).locator("..")).toContainText('active');
  })


  //checking OVERDUE (need to check color)
  await test.step("checking OVERDUE", async () => {
    await page.locator('input[name="deadline"]').fill('2025-05-01');
    await page.getByRole('button', { name: 'Edit' }).click();

    await expect(page.getByText(`${new_unique} 1234 edited`).locator("..")).toHaveCSS("background-color", "rgb(194, 62, 33)")
    await expect(page.getByText(`${new_unique} 1234 edited`).locator("..")).toContainText('overdue');
  })

  //checking COMPLETE (need to check color)
  await test.step("checking COMPLETE", async () => {
    await page.getByRole('checkbox', { name: 'Done?' }).check();
    await page.locator('input[name="deadline"]').fill('2026-05-01');
    await page.getByRole('button', { name: 'Edit' }).click();

    await expect(page.getByText(`${new_unique} 1234 edited`).locator("..")).toHaveCSS("background-color", "rgb(136, 185, 142)")
    await expect(page.getByText(`${new_unique} 1234 edited`).locator("..")).toContainText('completed');
    await page.getByText(`${new_unique} 1234 edited`).locator("..").click();
  })


  //checking macros !1
  await test.step("checking macros !1", async () => {
    await page.getByRole('textbox', { name: 'name' }).click();
    await page.getByRole('textbox', { name: 'name' }).fill(`${new_unique} macro !1`);
    await page.getByRole('button', { name: 'Create' }).click();
    await expect(page.getByText(`${new_unique} macro`).locator("..")).toContainText('critical');
  })


  //checking macro !before 01.01.2025
  await test.step("checking macro !before 01.01.2025", async () => {
    await page.getByRole('textbox', { name: 'name' }).click();
    await page.getByRole('textbox', { name: 'name' }).fill(`${new_unique} deadline !before 01.01.2025`);
    await page.getByRole('button', { name: 'Create' }).click();
    await expect(page.getByText(`${new_unique} deadline`).locator("..")).toContainText('to 2025-01-01');
  })

  //checking two macroses
  await test.step("checking two macroses", async () => {
    await page.getByRole('textbox', { name: 'name' }).click();
    await page.getByRole('textbox', { name: 'name' }).fill(`${new_unique} double !4 !before 02.02.2025`);
    await page.getByRole('button', { name: 'Create' }).click();
    await expect(page.getByText(`${new_unique} double`).locator("..")).toContainText('low');
    await expect(page.getByText(`${new_unique} double`).locator("..")).toContainText('to 2025-02-02');
  })


  //checking inputs priority
  await test.step("checking inputs priority", async () => {
    await page.getByRole('textbox', { name: 'name' }).click();
    await page.getByRole('textbox', { name: 'name' }).fill(`${new_unique} with priority !4 !before 02.02.2025`);
    await page.getByRole('combobox').selectOption('2');
    await page.locator('input[name="deadline"]').fill('2025-01-01');
    await page.getByRole('button', { name: 'Create' }).click();
    await expect(page.getByText(`${new_unique} with priority`).locator("..")).toContainText('high');
    await expect(page.getByText(`${new_unique} with priority`).locator("..")).toContainText('to 2025-01-01');
  })

  //checking sorting
  await test.step("checking sorting", async () => {
    await page.getByRole('button', { name: 'desc' }).click();
    await expect(page.getByRole('button', {name: 'asc'})).toBeAttached();
    await expect(page.locator('#task_list div').first()).toContainText('low');
  })

  //checking sorting by deadline
  await test.step("checking sorting by deadline", async () => {
    await page.getByRole('button', { name: 'priority' }).click();
    await expect(page.getByRole('button', {name: "deadline"})).toBeAttached();
    await expect(page.locator('#task_list div').first()).not.toHaveText("to ");
  })

  await test.step("checking deleting", async () => {
    await page.getByText("macro").click();
    await page.getByRole('button', { name: 'Delete' }).click();
    await expect(page.getByText("macro")).toHaveCount(0);
  })
})