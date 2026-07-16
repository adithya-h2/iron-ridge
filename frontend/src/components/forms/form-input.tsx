"use client";

import type { Control, FieldPath, FieldValues } from "react-hook-form";

import { Checkbox } from "@/components/ui/checkbox";
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

interface FormInputProps<T extends FieldValues> {
  control: Control<T>;
  name: FieldPath<T>;
  label: string;
  placeholder?: string;
  description?: string;
  type?: string;
}

export function FormInput<T extends FieldValues>({
  control,
  name,
  label,
  placeholder,
  description,
  type = "text",
}: FormInputProps<T>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input type={type} placeholder={placeholder} {...field} />
          </FormControl>
          {description ? <FormDescription>{description}</FormDescription> : null}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

interface FormCheckboxProps<T extends FieldValues> {
  control: Control<T>;
  name: FieldPath<T>;
  label: string;
  description?: string;
}

export function FormCheckbox<T extends FieldValues>({
  control,
  name,
  label,
  description,
}: FormCheckboxProps<T>) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
          <FormControl>
            <Checkbox checked={field.value} onCheckedChange={field.onChange} />
          </FormControl>
          <div className="space-y-1 leading-none">
            <FormLabel>{label}</FormLabel>
            {description ? <FormDescription>{description}</FormDescription> : null}
          </div>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
