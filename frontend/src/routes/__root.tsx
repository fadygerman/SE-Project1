import { createRootRoute, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import {AppSidebar} from "@/components/app-sidebar.tsx";
import {SidebarProvider} from "@/components/ui/sidebar.tsx";

export const Route = createRootRoute({
    component: () => (
        <div className="w-screen h-screen">
            <SidebarProvider>
                <AppSidebar />
                <hr />
                <Outlet />
                {/* <TanStackRouterDevtools /> */}
            </SidebarProvider>
        </div>
    ),
})